# Install each skill folder (the directory that contains SKILL.md) into
# the user-level Agent Skills paths. Category folders are skipped.

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Join-Path $Repo "skills"
if (-not (Test-Path $SkillRoot)) {
    throw "skills/ folder not found at $SkillRoot"
}

$dests = @(
    (Join-Path $HOME ".agents\skills"),
    (Join-Path $HOME ".cursor\skills"),
    (Join-Path $HOME ".codex\skills")
)

Get-ChildItem $SkillRoot -Recurse -Filter SKILL.md -File | ForEach-Object {
    $target = $_.Directory.FullName
    $name = $_.Directory.Name
    foreach ($dest in $dests) {
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        $link = Join-Path $dest $name
        if (Test-Path $link) {
            $item = Get-Item $link -Force
            $isReparse = [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
            if ($isReparse) {
                cmd /c rmdir "$link" | Out-Null
            } else {
                Write-Host "skip real directory $link"
                continue
            }
        }
        New-Item -ItemType Junction -Path $link -Target $target | Out-Null
        Write-Host "linked $link -> $target"
    }
}
