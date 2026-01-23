param(
    [Parameter(Mandatory=$true)][string]$FastaPath,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [int]$NumModels = 1,
    [int]$NumRecycle = 3,
    [string]$ModelType = "alphafold2_ptm",
    [switch]$EnableGpuRelax
)

# Validate Docker availability
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker CLI not found. Please install/start Docker Desktop and retry.";
    exit 1
}

# Resolve paths
$FastaPath = (Resolve-Path -Path $FastaPath).Path
$OutputDir = New-Item -ItemType Directory -Force -Path $OutputDir | Select-Object -ExpandProperty FullName

$inputParent = Split-Path -Path $FastaPath -Parent
$fastaLeaf   = Split-Path -Path $FastaPath -Leaf
$outParent   = Split-Path -Path $OutputDir -Parent
$outLeaf     = Split-Path -Path $OutputDir -Leaf

# GPU relax flag (default False to save VRAM)
$gpuRelaxFlag = if ($EnableGpuRelax.IsPresent) { "True" } else { "False" }

# Compose docker run
$inputParentEscaped = $inputParent -replace '\\', '/'
$outParentEscaped = $outParent -replace '\\', '/'
$dockerArgs = @(
    "run", "--rm", "--gpus", "all",
    "-v", "$inputParentEscaped`:/input",
    "-v", "$outParentEscaped`:/output",
    "ghcr.io/sokrypton/colabfold:1.5.5",
    "colabfold_batch",
    "--num-models", "$NumModels",
    "--num-recycle", "$NumRecycle",
    "--use-gpu-relax", "$gpuRelaxFlag",
    "--model-type", "$ModelType",
    "/input/$fastaLeaf",
    "/output/$outLeaf"
)

Write-Host "Running ColabFold in Docker..." -ForegroundColor Cyan
Write-Host "Input:  $FastaPath"
Write-Host "Output: $OutputDir"

# Execute
& docker @dockerArgs
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Error "ColabFold Docker run failed with exit code $exitCode"
    exit $exitCode
}

Write-Host "Completed. Results in $OutputDir" -ForegroundColor Green
