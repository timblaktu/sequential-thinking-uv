{
  description = "Sequential-Thinking MCP Server with uv2nix integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    ...
  }: let
    inherit (nixpkgs) lib;

    # Load a uv workspace from a workspace root.
    workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

    # Create package overlay from workspace.
    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel"; # Prefer prebuilt binary wheels
    };

    # Extend generated overlay with build fixups
    pyprojectOverrides = _final: _prev: {
      # Build fixups for sequential-thinking-mcp if needed
    };

    # Support multiple systems
    systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
    forAllSystems = lib.genAttrs systems;

  in {
    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;

      # Construct package set
      pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
        inherit python;
      }).overrideScope (
        lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
          pyprojectOverrides
        ]
      );
    in {
      default = pythonSet.mkVirtualEnv "sequential-thinking-mcp-env" workspace.deps.default;
      sequential-thinking-mcp = pythonSet.mkVirtualEnv "sequential-thinking-mcp-env" workspace.deps.default;
    });

    apps = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/sequential-thinking-mcp";
      };
      sequential-thinking-mcp = {
        type = "app";
        program = "${self.packages.${system}.sequential-thinking-mcp}/bin/sequential-thinking-mcp";
      };
    });

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;
    in {
      default = pkgs.mkShell {
        packages = with pkgs; [
          python
          uv
          git
          # Development tools
          ruff
          black
          mypy
        ];
        
        env = {
          UV_PYTHON_DOWNLOADS = "never";
          UV_PYTHON = python.interpreter;
        } // lib.optionalAttrs pkgs.stdenv.isLinux {
          LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
        };
        
        shellHook = ''
          unset PYTHONPATH
          echo "=== Sequential-Thinking MCP Server Development Environment ==="
          echo "Python: $(python --version)"
          echo "UV: $(uv --version)"
          echo
          echo "Development commands:"
          echo "  uv sync --dev       # Install dependencies"
          echo "  uv run pytest      # Run tests"
          echo "  uv run sequential-thinking-mcp  # Run server"
          echo "  nix build           # Build with Nix"
          echo "  nix run             # Run with Nix"
          echo
          echo "Sequential-Thinking MCP Server ready for development!"
        '';
      };
    });

    checks = forAllSystems (system: {
      # Build the package to ensure it works
      build = self.packages.${system}.default;
    });
  };
}
