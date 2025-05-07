
# Mod Build & Release Workflows

This repository contains GitHub Actions workflows for building and releasing mods.

## Versioning

This CI/CD system uses GitHub's Semantic Versioning (SemVer). Version numbers are automatically incremented based on commit message prefixes:

- `+semver:` + `major` or `breaking` - Increments major version (x.0.0)
- `+semver:` + `minor` or `feature` - Increments minor version (0.x.0) 
- `+semver:` + `patch` or `fix` - Increments patch version (0.0.x)

Examples:
```
git commit -m "add new weapon system +semver:minor "  # 1.1.0 -> 1.2.0
git commit -m "correct damage values +semver:patch"  # 1.2.0 -> 1.2.1
git commit -m "rework mod API +semver:major"         # 1.2.1 -> 2.0.0
```

## Mod Build Workflow

The `mod-build.yml` workflow handles building your mod and creating GitHub releases.

### Usage

```yaml
name: Build

on:
  push:
    branches: [ main, master ]

permissions:
  contents: write

jobs:
  build:
    uses: CrimsonMods/actions/.github/workflows/mod-build.yml@master
    with:
      artifact-path: ./bin/Release/net6.0/YourMod.dll
      project-name: YourModName
```

### Parameters

- `dotnet-versions`: .NET SDK versions to setup (default: 6.0.x and 8.0.x)
- `artifact-path`: Path to your built DLL file (required)
- `project-name`: Name of your project (required)
- `create-release`: Whether to create a GitHub release (default: true)
- `changelog-path`: Path to changelog file (default: CHANGELOG.md)
- `release-files`: Additional files to include in release
- `build-configuration`: Build configuration (default: Release)

## Mod Release Workflow

The `mod-release.yml` workflow handles publishing releases to Thunderstore.

### Usage

```yaml
name: Release
on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      tag_name:
        required: true
        description: The tag to release.
        type: string

permissions:
  contents: write
  packages: write

jobs:
  release:
    uses: CrimsonMods/actions/.github/workflows/mod-release.yml@master
    with:
      release-tag: ${{ github.event_name == 'workflow_dispatch' && inputs.tag_name || github.ref_name }}
    secrets:
      thunderstore-key: ${{ secrets.THUNDERSTORE_KEY }}
```

### Parameters

- `release-tag`: Tag to release (required)
- `dotnet-version`: .NET SDK version (default: 6.0.x)
- `download-directory`: Directory to download release files to (default: ./dist)
- `artifact-directory`: Directory to upload as artifact (default: ./build)
- `package-config-path`: Optional custom path to thunderstore package config

### Secrets

- `thunderstore-key`: Thunderstore API key (required)

## Dependency Update Workflow

The `dependency-update.yml` workflow handles automated NuGet package updates.

### Usage

```yaml
name: Update Dependencies

on:
  schedule:
    - cron: '0 0 * * 0'  # Run weekly

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    uses: CrimsonMods/actions/.github/workflows/dependency-update.yml@master
    with:
      project-path: ./YourMod.csproj
```

[What is cron?](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)

### Parameters

- `project-path`: Path to your .csproj file (required)
- `target-branch`: Branch to create PRs against (default: main)
- `dotnet-version`: .NET SDK version (default: 6.0.x)
- `include-prerelease`: Whether to include prerelease packages (default: false)
- `specific-packages`: Space-separated list of specific packages to update (default: all packages)
