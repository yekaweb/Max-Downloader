@echo off
REM Archived to bat_archive/create_structure.bat
REM Use the archived copy instead of this root file.
REM Create DLBot project directory structure
REM Run this from the project root directory

REM Core bot directories
mkdir bot
mkdir bot\middlewares
mkdir bot\handlers
mkdir bot\handlers\admin
mkdir bot\keyboards
mkdir bot\keyboards\inline
mkdir bot\keyboards\reply
mkdir bot\states
mkdir bot\filters

REM Modules
mkdir modules
mkdir modules\youtube
mkdir modules\instagram
mkdir modules\twitter
mkdir modules\direct_link

REM Services and tasks
mkdir services
mkdir tasks

REM Database
mkdir database
mkdir database\models
mkdir database\repositories

REM Web panel
mkdir web
mkdir web\routers
mkdir web\templates
mkdir web\static
mkdir web\static\css
mkdir web\static\js

REM Locales
mkdir locales
mkdir locales\fa
mkdir locales\en
mkdir locales\ar
mkdir locales\ru
mkdir locales\zh

REM Utilities
mkdir utils
mkdir migrations
mkdir migrations\versions
mkdir logs
mkdir temp_downloads
mkdir cached_files

REM Create __init__.py files for each Python package
REM Bot package
echo. > bot\__init__.py
echo. > bot\middlewares\__init__.py
echo. > bot\handlers\__init__.py
echo. > bot\handlers\admin\__init__.py
echo. > bot\keyboards\__init__.py
echo. > bot\keyboards\inline\__init__.py
echo. > bot\keyboards\reply\__init__.py
echo. > bot\states\__init__.py
echo. > bot\filters\__init__.py

REM Modules package
echo. > modules\__init__.py
echo. > modules\youtube\__init__.py
echo. > modules\instagram\__init__.py
echo. > modules\twitter\__init__.py
echo. > modules\direct_link\__init__.py

REM Other packages
echo. > services\__init__.py
echo. > tasks\__init__.py
echo. > database\__init__.py
echo. > database\models\__init__.py
echo. > database\repositories\__init__.py
echo. > web\__init__.py
echo. > web\routers\__init__.py
echo. > utils\__init__.py
echo. > migrations\__init__.py

echo.
echo ✅ Project directory structure created successfully!
