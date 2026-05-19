@echo off
setlocal enabledelayedexpansion

:: --- Config ---
set USE_EXTRA_DATA=true

:: --- Environment Setup ---
call venv\Scripts\activate.bat

if not exist checkpoints mkdir checkpoints
if not exist archives    mkdir archives
if not exist data        mkdir data

:: --- Generation Checkpoint Handling ---
if not exist checkpoints\generation.txt (
    > checkpoints\generation.txt echo 1
)
set /p GENERATION=<checkpoints\generation.txt 2>nul
if not defined GENERATION set GENERATION=1
set GENERATION=%GENERATION: =%

:: --- How many iterations to run? ---
set /p ITERATIONS=How many generations to run? 

:: --- User Confirmation ---
echo WARNING: This will delete all existing logs in the logs folder each iteration.
set /p confirm=Are you sure? (y/n): 
if /i "%confirm%" neq "y" (
    echo Aborted.
    pause
    exit /b
)

:: --- Main Loop ---
for /l %%I in (1,1,%ITERATIONS%) do (
    set /p GENERATION=<checkpoints\generation.txt
    set GENERATION=!GENERATION: =!
    if "!GENERATION!"=="" set GENERATION=1
    set /a NEXT_GENERATION=!GENERATION!+1

    echo.
    echo ==========================================
    echo ITERATION %%I of %ITERATIONS% ^| Generation !GENERATION!
    echo ==========================================

    :: --- Self-Play Data Generation ---
    echo Clearing old logs...
    if exist logs\*.csv del /q logs\*.csv 2>nul

    echo Generating self-play games...
    python simulate_games.py -num_games 2000 -player1_type MCTSNNAIPlayer -player2_type MCTSNNAIPlayer --enable_logs --parallel

    echo Merging self-play CSV files...
    python .\ml_utils\flatten_csv_logs.py -name data\self_play_data.csv

    echo Archiving generation !GENERATION!...
    python .\ml_utils\archive_gen_dataset.py -source data\self_play_data.csv -generation !GENERATION!


    :: --- Combine ---
    if exist logs\*.csv del /q logs\*.csv 2>nul

    if /i "%USE_EXTRA_DATA%"=="true" (
        echo Combining datasets...
        python .\ml_utils\combine_datasets.py -inputs data\self_play_data.csv data\discard_move_data.csv -output data\move_data.csv
    ) else (
        copy data\self_play_data.csv data\move_data.csv >nul
    )

    :: --- Training ---
    echo Training model for Generation !GENERATION!...
    if exist value_net_best.pth (
        python train.py -model value_net_best.pth
    ) else (
        echo No existing model found, training from scratch...
        python train.py
    )

    :: --- Backup and Benchmarking ---
    echo Saving generation checkpoint...
    if not exist "checkpoints\gen_!GENERATION!" mkdir "checkpoints\gen_!GENERATION!"
    copy value_net_best.pth "checkpoints\gen_!GENERATION!\value_net.pth" >nul
    copy value_net_best.pth "checkpoints\gen_!GENERATION!\value_net_best.pth" >nul

    echo Benchmarking generation !GENERATION!...
    echo ------------------------------------------ >> checkpoints\benchmark_log.txt
    echo Generation !GENERATION! vs RuleBasedAIPlayer: >> checkpoints\benchmark_log.txt
    python simulate_games.py -num_games 1000 -player1_type MCTSNNAIPlayer -player2_type RuleBasedAIPlayer --parallel >> checkpoints\benchmark_log.txt

    :: --- Advance Generation ---
    echo !NEXT_GENERATION! > checkpoints\generation.txt
    echo Done. Generation !GENERATION! complete.
)

echo.
echo ==========================================
echo All %ITERATIONS% iterations complete!
echo ==========================================
pause