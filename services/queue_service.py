"""
🔴 Phase 5: Queue Management System
Purpose: Priority-based task queuing, resource management, and orchestration
Goal: 60% reduction in wait time

Components:
- PriorityQueueManager: Priority-based task queuing with fair scheduling
- ResourceManager: CPU, memory, bandwidth monitoring and dynamic adjustment
- UnifiedDownloadOrchestrator: Coordinates all 5 phases into one workflow
"""

from __future__ import annotations

import asyncio
import heapq
import logging
import psutil
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


# ============================================================================
# PRIORITY QUEUE SYSTEM
# ============================================================================

class Priority(Enum):
    """اولویت‌های انجام کار"""
    CRITICAL = 0  # سیستم/ادمین
    HIGH = 1      # کاربران Premium
    NORMAL = 2    # کاربران معمول
    LOW = 3       # کاربران رایگان


@dataclass
class DownloadTask:
    """یک task دانلود در صف"""
    priority: Priority
    timestamp: float  # زمان اضافه شدن (برای FIFO اگر priority برابر)
    user_id: int
    url: str
    chat_id: int
    file_format: str = 'auto'
    compression_enabled: bool = False
    compression_quality: str = 'medium'
    stream_upload: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "DownloadTask") -> bool:
        """برای heap sorting - اولویت بالاتر اول، سپس زمان"""
        if self.priority.value == other.priority.value:
            return self.timestamp < other.timestamp
        return self.priority.value < other.priority.value

    def __eq__(self, other: "DownloadTask") -> bool:
        """برای مقایسه tasks"""
        return (self.user_id == other.user_id and 
                self.url == other.url and 
                self.chat_id == other.chat_id)


@dataclass
class TaskStatus:
    """وضعیت یک task"""
    task_id: str
    user_id: int
    url: str
    status: str  # 'queued', 'processing', 'completed', 'failed'
    position_in_queue: int = 0
    estimated_wait_time: int = 0  # به ثانیه
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: int = 0  # 0-100


class PriorityQueueManager:
    """
    مدیر صف اولویت‌دار برای دانلودها
    
    ویژگی‌ها:
    - اولویت‌بندی بر اساس user type (Premium vs Free)
    - FIFO برای کاربران یکسان اولویت
    - محدود کردن tasks همزمان (max_concurrent)
    - ردیابی موقعیت کاربر در صف
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Args:
            max_concurrent: حداکثر tasks همزمان برای پردازش
        """
        self.queue: List[DownloadTask] = []
        self.active_tasks: Dict[str, TaskStatus] = {}
        self.completed_tasks: Dict[str, TaskStatus] = {}
        self.max_concurrent = max_concurrent
        self.lock = asyncio.Lock()
        self.task_counter = 0

    async def add_task(self, task: DownloadTask) -> tuple[str, int]:
        """
        افزودن task به صف و بازگرداندن ID و موقعیت
        
        Args:
            task: DownloadTask برای اضافه کردن
            
        Returns:
            (task_id, position_in_queue)
        """
        async with self.lock:
            self.task_counter += 1
            task_id = f"task_{task.user_id}_{self.task_counter}_{int(datetime.utcnow().timestamp())}"
            
            heapq.heappush(self.queue, task)
            position = len(self.queue)
            
            logger.info(f"[PHASE 5] Task {task_id} added to queue at position {position}")
            
            return task_id, position

    async def get_next_task(self) -> Optional[tuple[str, DownloadTask]]:
        """
        گرفتن task بعدی برای پردازش
        
        بررسی می‌کند که آیا جای خالی است برای task جدید
        
        Returns:
            (task_id, task) یا None اگر نتوان
        """
        async with self.lock:
            # چک کنید که جای خالی هست
            if len(self.active_tasks) >= self.max_concurrent:
                logger.debug(f"[PHASE 5] Max concurrent tasks ({self.max_concurrent}) reached")
                return None
            
            # صف خالی است
            if not self.queue:
                logger.debug("[PHASE 5] Queue is empty")
                return None
            
            # گرفتن بعدی
            task = heapq.heappop(self.queue)
            task_id = f"task_{task.user_id}_{self.task_counter}_{int(datetime.utcnow().timestamp())}"
            
            # ثبت شروع
            status = TaskStatus(
                task_id=task_id,
                user_id=task.user_id,
                url=task.url,
                status='processing',
                start_time=datetime.utcnow(),
                position_in_queue=0  # اکنون پردازش می‌شود
            )
            self.active_tasks[task_id] = status
            
            logger.info(f"[PHASE 5] Task {task_id} started processing")
            
            return task_id, task

    async def complete_task(self, task_id: str, success: bool = True, error: str = None):
        """
        نشانه‌گذاری task به عنوان تکمیل‌شده
        
        Args:
            task_id: ID تسک
            success: آیا موفق بود
            error: پیام خطا (اگر ناموفق)
        """
        async with self.lock:
            if task_id not in self.active_tasks:
                logger.warning(f"[PHASE 5] Task {task_id} not found in active tasks")
                return
            
            status = self.active_tasks[task_id]
            status.end_time = datetime.utcnow()
            status.status = 'completed' if success else 'failed'
            status.error_message = error
            status.progress = 100 if success else 0
            
            # منتقل به completed
            self.completed_tasks[task_id] = status
            del self.active_tasks[task_id]
            
            result = "✅ completed" if success else f"❌ failed: {error}"
            logger.info(f"[PHASE 5] Task {task_id} {result}")

    async def update_task_progress(self, task_id: str, progress: int):
        """
        آپدیت تقدم یک task
        
        Args:
            task_id: ID تسک
            progress: درصد تقدم (0-100)
        """
        if task_id in self.active_tasks:
            self.active_tasks[task_id].progress = min(100, max(0, progress))

    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        گرفتن وضعیت یک task
        
        Args:
            task_id: ID تسک
            
        Returns:
            TaskStatus یا None
        """
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        return None

    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        آمار صف
        
        Returns:
            Dict with:
            - queue_length: تعداد tasks در صف
            - active_tasks: تعداد tasks درحال پردازش
            - avg_wait_time: متوسط زمان انتظار
            - estimated_wait_for_new: تخمین انتظار برای task جدید
        """
        async with self.lock:
            queue_length = len(self.queue)
            active_count = len(self.active_tasks)
            
            # تخمین: هر task ~120-180 ثانیه
            avg_task_duration = 150  # 2.5 دقیقه
            estimated_wait = queue_length * avg_task_duration
            
            return {
                'queue_length': queue_length,
                'active_tasks': active_count,
                'max_concurrent': self.max_concurrent,
                'total_available_slots': self.max_concurrent - active_count,
                'estimated_wait_seconds': estimated_wait,
                'estimated_wait_minutes': estimated_wait // 60,
                'completed_tasks': len(self.completed_tasks)
            }

    async def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """
        گرفتن تمام tasks یک کاربر
        
        Args:
            user_id: شناسه کاربر
            
        Returns:
            لیست tasks کاربر
        """
        async with self.lock:
            tasks = []
            
            # تسک‌های فعال
            for task_id, status in self.active_tasks.items():
                if status.user_id == user_id:
                    tasks.append({
                        'task_id': task_id,
                        'status': status.status,
                        'progress': status.progress,
                        'url': status.url
                    })
            
            # تسک‌های تکمیل شده
            for task_id, status in self.completed_tasks.items():
                if status.user_id == user_id:
                    tasks.append({
                        'task_id': task_id,
                        'status': status.status,
                        'url': status.url,
                        'completed_at': status.end_time
                    })
            
            return tasks


# ============================================================================
# RESOURCE MANAGEMENT SYSTEM
# ============================================================================

class ResourceManager:
    """
    مدیر منابع - نظارت بر CPU, Memory, Bandwidth
    
    ویژگی‌ها:
    - نظارت مستمر بر استفاده منابع
    - تنظیم dynamic max_concurrent بر اساس منابع
    - سیگنال به queue manager برای کاهش/افزایش
    - Health status reporting
    """

    def __init__(self):
        self.cpu_usage: float = 0
        self.memory_usage: float = 0
        self.disk_usage: float = 0
        self.bandwidth_usage: float = 0
        self.is_healthy: bool = True
        self.lock = asyncio.Lock()
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """شروع نظارت منابع"""
        if self.monitoring:
            logger.warning("[PHASE 5] Resource monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("[PHASE 5] Resource monitoring started")

    async def stop_monitoring(self):
        """توقف نظارت منابع"""
        self.monitoring = False
        if self.monitor_task:
            await self.monitor_task
        logger.info("[PHASE 5] Resource monitoring stopped")

    async def _monitor_loop(self):
        """حلقه نظارت مستمر"""
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()

        while self.monitoring:
            try:
                # اجرای بررسی منابع در thread جداگانه
                resources = await loop.run_in_executor(
                    executor,
                    self._check_resources
                )
                
                async with self.lock:
                    self.cpu_usage = resources['cpu']
                    self.memory_usage = resources['memory']
                    self.disk_usage = resources['disk']
                    self.is_healthy = resources['healthy']
                
                if not self.is_healthy:
                    logger.warning(
                        f"[PHASE 5] Resource stress detected - "
                        f"CPU: {self.cpu_usage}%, Memory: {self.memory_usage}%, "
                        f"Disk: {self.disk_usage}%"
                    )
                
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"[PHASE 5] Error in resource monitoring: {e}")
                await asyncio.sleep(5)

    def _check_resources(self) -> Dict[str, Any]:
        """بررسی منابع (blocking - برای ThreadPoolExecutor)"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # تعریف healthy: CPU < 70%, Memory < 75%, Disk < 80%
            healthy = cpu < 70 and memory < 75 and disk < 80
            
            return {
                'cpu': cpu,
                'memory': memory,
                'disk': disk,
                'healthy': healthy
            }
        except Exception as e:
            logger.error(f"[PHASE 5] Error checking resources: {e}")
            return {
                'cpu': 0,
                'memory': 0,
                'disk': 0,
                'healthy': True
            }

    async def get_resource_status(self) -> Dict[str, Any]:
        """
        گرفتن وضعیت منابع
        
        Returns:
            Dict with resource percentages and health status
        """
        async with self.lock:
            status = 'healthy' if self.is_healthy else 'stressed'
            
            return {
                'cpu_percent': round(self.cpu_usage, 1),
                'memory_percent': round(self.memory_usage, 1),
                'disk_percent': round(self.disk_usage, 1),
                'status': status,
                'can_process': self.is_healthy,
                'recommendation': self._get_recommendation()
            }

    def _get_recommendation(self) -> str:
        """توصیه برای بهبود منابع"""
        if self.cpu_usage > 85:
            return "CPU critical - reduce concurrent tasks"
        elif self.cpu_usage > 70:
            return "CPU high - consider reducing tasks"
        elif self.memory_usage > 85:
            return "Memory critical - reduce concurrent tasks"
        elif self.memory_usage > 75:
            return "Memory high - monitor usage"
        else:
            return "Resources normal"

    async def should_accept_new_task(self) -> bool:
        """
        آیا می‌توان task جدید قبول کرد
        
        Returns:
            True اگر منابع کافی هستند
        """
        async with self.lock:
            return self.is_healthy


# ============================================================================
# UNIFIED DOWNLOAD ORCHESTRATOR
# ============================================================================

class UnifiedDownloadOrchestrator:
    """
    نقطه مرکزی برای هماهنگی تمام 5 phases
    
    جریان:
    1. Task اضافه به صف
    2. منتظر نوبت
    3. دانلود (Phase 2)
    4. فشرده‌سازی (Phase 4)
    5. آپلود به Telegram (Phase 3)
    6. نوتیفیکیشن کاربر
    """

    def __init__(self):
        self.queue_manager = PriorityQueueManager(max_concurrent=3)
        self.resource_manager = ResourceManager()
        self.task_callbacks: Dict[str, List[Callable]] = {
            'queued': [],
            'started': [],
            'progress': [],
            'completed': [],
            'failed': []
        }
        logger.info("[PHASE 5] UnifiedDownloadOrchestrator initialized")

    async def initialize(self):
        """راه‌اندازی orchestrator"""
        await self.resource_manager.start_monitoring()
        logger.info("[PHASE 5] Orchestrator initialized and monitoring started")

    async def shutdown(self):
        """خاموش کردن orchestrator"""
        await self.resource_manager.stop_monitoring()
        logger.info("[PHASE 5] Orchestrator shutdown")

    def register_callback(self, event: str, callback: Callable):
        """
        ثبت callback برای events
        
        Args:
            event: نام event ('queued', 'started', 'progress', 'completed', 'failed')
            callback: تابع callback
        """
        if event in self.task_callbacks:
            self.task_callbacks[event].append(callback)

    async def _trigger_callbacks(self, event: str, **kwargs):
        """فعال‌سازی callbacks برای یک event"""
        for callback in self.task_callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)
            except Exception as e:
                logger.error(f"[PHASE 5] Error in {event} callback: {e}")

    async def enqueue_download(
        self,
        user_id: int,
        url: str,
        chat_id: int,
        priority: Priority = Priority.NORMAL,
        **kwargs
    ) -> tuple[str, int]:
        """
        افزودن دانلود به صف
        
        Args:
            user_id: شناسه کاربر
            url: آدرس دانلود
            chat_id: شناسه چت Telegram
            priority: اولویت
            **kwargs: options اضافی (compression, format, etc)
            
        Returns:
            (task_id, position_in_queue)
        """
        task = DownloadTask(
            priority=priority,
            timestamp=datetime.utcnow().timestamp(),
            user_id=user_id,
            url=url,
            chat_id=chat_id,
            file_format=kwargs.get('file_format', 'auto'),
            compression_enabled=kwargs.get('compression_enabled', False),
            compression_quality=kwargs.get('compression_quality', 'medium'),
            stream_upload=kwargs.get('stream_upload', False),
            metadata=kwargs.get('metadata', {})
        )
        
        task_id, position = await self.queue_manager.add_task(task)
        
        # Trigger callback
        await self._trigger_callbacks(
            'queued',
            task_id=task_id,
            user_id=user_id,
            position=position,
            url=url
        )
        
        logger.info(f"[PHASE 5] Download enqueued: {task_id} at position {position}")
        return task_id, position

    async def process_queue(
        self,
        download_handler: Callable,
        compress_handler: Callable = None,
        upload_handler: Callable = None
    ):
        """
        پردازش مستمر صف
        
        Args:
            download_handler: تابع برای دانلود
            compress_handler: تابع برای فشرده‌سازی (optional)
            upload_handler: تابع برای آپلود (optional)
        """
        logger.info("[PHASE 5] Queue processing started")
        
        while True:
            try:
                # چک منابع
                can_process = await self.resource_manager.should_accept_new_task()
                if not can_process:
                    logger.warning("[PHASE 5] Resources stressed, pausing queue processing")
                    await asyncio.sleep(10)
                    continue
                
                # گرفتن task بعدی
                result = await self.queue_manager.get_next_task()
                if not result:
                    await asyncio.sleep(2)
                    continue
                
                task_id, task = result
                
                try:
                    # Trigger started callback
                    await self._trigger_callbacks(
                        'started',
                        task_id=task_id,
                        user_id=task.user_id,
                        url=task.url
                    )
                    
                    # 1. دانلود (Phase 2)
                    logger.info(f"[PHASE 5] Starting download for task {task_id}")
                    download_result = await download_handler(
                        url=task.url,
                        file_format=task.file_format,
                        progress_callback=lambda p: self.queue_manager.update_task_progress(task_id, p * 30)
                    )
                    
                    if not download_result['success']:
                        raise Exception(f"Download failed: {download_result.get('error')}")
                    
                    file_path = download_result['file_path']
                    
                    # 2. فشرده‌سازی (Phase 4) - اختیاری
                    if task.compression_enabled and compress_handler:
                        logger.info(f"[PHASE 5] Starting compression for task {task_id}")
                        compress_result = await compress_handler(
                            input_path=file_path,
                            quality=task.compression_quality,
                            progress_callback=lambda p: self.queue_manager.update_task_progress(task_id, 30 + (p * 30))
                        )
                        
                        if compress_result['success']:
                            file_path = compress_result['output_path']
                    
                    # 3. آپلود (Phase 3) - اختیاری
                    if task.stream_upload and upload_handler:
                        logger.info(f"[PHASE 5] Starting upload for task {task_id}")
                        upload_result = await upload_handler(
                            file_path=file_path,
                            chat_id=task.chat_id,
                            progress_callback=lambda p: self.queue_manager.update_task_progress(task_id, 60 + (p * 40))
                        )
                        
                        if not upload_result['success']:
                            raise Exception(f"Upload failed: {upload_result.get('error')}")
                    
                    # 4. موفق
                    await self.queue_manager.complete_task(task_id, success=True)
                    
                    await self._trigger_callbacks(
                        'completed',
                        task_id=task_id,
                        user_id=task.user_id,
                        file_path=file_path
                    )
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"[PHASE 5] Task {task_id} failed: {error_msg}")
                    
                    await self.queue_manager.complete_task(task_id, success=False, error=error_msg)
                    
                    await self._trigger_callbacks(
                        'failed',
                        task_id=task_id,
                        user_id=task.user_id,
                        error=error_msg
                    )
                
            except Exception as e:
                logger.error(f"[PHASE 5] Error in queue processing: {e}")
                await asyncio.sleep(5)

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        گرفتن وضعیت کامل صف و سیستم
        
        Returns:
            Dict with queue and resource status
        """
        queue_stats = await self.queue_manager.get_queue_stats()
        resource_status = await self.resource_manager.get_resource_status()
        
        return {
            'queue': queue_stats,
            'resources': resource_status,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """
        گرفتن وضعیت کاربر در سیستم
        
        Args:
            user_id: شناسه کاربر
            
        Returns:
            Dict with user's task status
        """
        tasks = await self.queue_manager.get_user_tasks(user_id)
        
        return {
            'user_id': user_id,
            'active_tasks': [t for t in tasks if t['status'] == 'processing'],
            'queued_tasks': [t for t in tasks if t['status'] == 'queued'],
            'completed_tasks': [t for t in tasks if t['status'] == 'completed'],
            'failed_tasks': [t for t in tasks if t['status'] == 'failed'],
            'total_tasks': len(tasks)
        }


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_queue_manager: Optional[PriorityQueueManager] = None
_resource_manager: Optional[ResourceManager] = None
_orchestrator: Optional[UnifiedDownloadOrchestrator] = None


def get_queue_manager() -> PriorityQueueManager:
    """گرفتن singleton queue manager"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = PriorityQueueManager()
    return _queue_manager


def get_resource_manager() -> ResourceManager:
    """گرفتن singleton resource manager"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def get_orchestrator() -> UnifiedDownloadOrchestrator:
    """گرفتن singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = UnifiedDownloadOrchestrator()
    return _orchestrator


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'Priority',
    'DownloadTask',
    'TaskStatus',
    'PriorityQueueManager',
    'ResourceManager',
    'UnifiedDownloadOrchestrator',
    'get_queue_manager',
    'get_resource_manager',
    'get_orchestrator',
]
