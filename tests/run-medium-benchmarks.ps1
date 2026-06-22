# Run each medium benchmark problem with every solver a few times and print average time.
param(
    [int]$Runs = 6,
    [string[]]$SolverConfigurations = @(
        'psimplex',
        'dsimplex',
        'gsimplex',
        'gsimplex-rel-gap-0.1',
        'msimplex',
        'msimplex-rel-gap-0.1'
    ),
    [string]$ProblemsPath = "$PSScriptRoot\problems\medium",
    [string]$CsvOutput = "$PSScriptRoot\benchmark-results.csv"
)

if (-not (Test-Path $ProblemsPath)) {
    Write-Error "Problem directory not found: $ProblemsPath"
    exit 1
}

$allSolverConfigs = @(
    [pscustomobject]@{
        Name = 'psimplex'
        Solver = 'psimplex'
        ExtraArgs = @()
    },
    [pscustomobject]@{
        Name = 'dsimplex'
        Solver = 'dsimplex'
        ExtraArgs = @()
    },
    [pscustomobject]@{
        Name = 'gsimplex'
        Solver = 'gsimplex'
        ExtraArgs = @('--rel-gap', '0.0')
    },
    [pscustomobject]@{
        Name = 'gsimplex-rel-gap-0.1'
        Solver = 'gsimplex'
        ExtraArgs = @('--rel-gap', '0.1')
    },
    [pscustomobject]@{
        Name = 'msimplex'
        Solver = 'msimplex'
        ExtraArgs = @('--rel-gap', '0.0')
    },
    [pscustomobject]@{
        Name = 'msimplex-rel-gap-0.1'
        Solver = 'msimplex'
        ExtraArgs = @('--rel-gap', '0.1')
    }
)

$solverConfigs = $allSolverConfigs | Where-Object { $SolverConfigurations -contains $_.Name }
if ($solverConfigs.Count -eq 0) {
    Write-Error "No solver configurations selected."
    exit 1
}

$problems = @(
    [pscustomobject]@{
        FileName = '10x02.mps'
        Sense = 'maximize'
        ExpectedValue = 8068.4059
    },
    [pscustomobject]@{
        FileName = '10x04.mps'
        Sense = 'minimize'
        ExpectedValue = 468.1287
    },
    [pscustomobject]@{
        FileName = '13x05.mps'
        Sense = 'maximize'
        ExpectedValue = 3120.5018
    },
    [pscustomobject]@{
        FileName = '21x08.mps'
        Sense = 'minimize'
        ExpectedValue = 319.4278
    },
    [pscustomobject]@{
        FileName = '34x15.mps'
        Sense = 'minimize'
        ExpectedValue = 264.0395
    },
    [pscustomobject]@{
        FileName = '34x15.mps'
        Sense = 'maximize'
        ExpectedValue = 3195.6684
    },
    [pscustomobject]@{
        FileName = '28x21.mps'
        Sense = 'maximize'
        ExpectedValue = 673.5980
    },
    [pscustomobject]@{
        FileName = '47x45.mps'
        Sense = 'maximize'
        ExpectedValue = 9953.3270
    },
    [pscustomobject]@{
        FileName = '65x56.mps'
        Sense = 'maximize'
        ExpectedValue = 16192.0848
    },
    [pscustomobject]@{
        FileName = '88x73.mps'
        Sense = 'maximize'
        ExpectedValue = 15370.6017
    }
)

if (-not (Get-Command gsimplex -ErrorAction SilentlyContinue)) {
    Write-Error "Command 'gsimplex' not found. Please install the package and ensure the command is on PATH."
    exit 1
}

function Invoke-GSimplexCommand {
    param(
        [string]$ProblemFile,
        [string]$Solver,
        [string[]]$ExtraArgs,
        [string]$ConfigName,
        [object]$KnownValue,
        [string]$Sense
    )

    $_Args = @(
        "--problem", $ProblemFile,
        "--solver", $Solver,
        "--quiet",
        "--sense", $Sense
    )
    $_Args += $ExtraArgs

    if ($ConfigName -eq 'msimplex-rel-gap-0.1' -and $null -ne $KnownValue) {
        if ($Sense -eq 'maximize') {
            $_Args += @('--ub', "$KnownValue")
        } elseif ($Sense -eq 'minimize') {
            $_Args += @('--lb', "$KnownValue")
        }
    }

    return & gsimplex @_Args 2>&1
}

Write-Host "Running $Runs runs for each solver on each medium problem..."
Write-Host "Problem directory: $ProblemsPath"
Write-Host "Solver configurations: $($solverConfigs.Name -join ', ')"
Write-Host ""

$summary = @()
foreach ($problem in $problems) {
    $problemPath = Join-Path $ProblemsPath $problem.FileName
    if (-not (Test-Path $problemPath)) {
        Write-Error "Problem file not found: $problemPath"
        continue
    }

    $expectedText = if ($null -ne $problem.ExpectedValue) { $problem.ExpectedValue } else { 'unknown' }
    Write-Host "Problem: $($problem.FileName) (sense=$($problem.Sense), expected=$expectedText)"

    foreach ($config in $solverConfigs) {
        $times = @()
        for ($i = 1; $i -le $Runs; $i++) {
            Write-Host "  [$($config.Name)] Run $i/$Runs..." -NoNewline
            $output = Invoke-GSimplexCommand -ProblemFile $problemPath -Solver $config.Solver -ExtraArgs $config.ExtraArgs -ConfigName $config.Name -KnownValue $problem.ExpectedValue -Sense $problem.Sense
            $exitCode = $LASTEXITCODE

            if ($exitCode -ne 0) {
                Write-Host " failed (exit code $exitCode)"
                Write-Host $output
                break
            }

            $match = [regex]::Match($output, 'Time:\s*([0-9]+(?:\.[0-9]+)?)', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if (-not $match.Success) {
                Write-Host " failed to parse time"
                Write-Host $output
                break
            }

            $time = [double]$match.Groups[1].Value
            $times += $time
            Write-Host " done ($time sec)"
        }

        if ($times.Count -gt 0) {
            $average = ($times | Measure-Object -Average).Average
            $average = [math]::Round($average, 6)
            Write-Host "  => Average ($($config.Name)): $average seconds`n"
            $summary += [pscustomobject]@{
                Problem = $problem.FileName
                Sense = $problem.Sense
                ExpectedValue = $problem.ExpectedValue
                Config = $config.Name
                Solver = $config.Solver
                AverageTime = $average
            }
        }
    }
}

Write-Host "Benchmark summary:`n"
$summary | Sort-Object Config, Problem | Format-Table -AutoSize

# Export CSV with problems as columns and solver configurations as rows
$csvRows = @()
foreach ($config in $solverConfigs) {
    $row = [ordered]@{ SolverConfig = $config.Name }
    foreach ($problem in $problems) {
        $entry = $summary | Where-Object { $_.Config -eq $config.Name -and $_.Problem -eq $problem.FileName } | Select-Object -First 1
        $row[$problem.FileName] = if ($entry) { $entry.AverageTime } else { '' }
    }
    $csvRows += New-Object psobject -Property $row
}

$csvRows | Export-Csv -Path $CsvOutput -NoTypeInformation
Write-Host "Saved CSV results to $CsvOutput"
