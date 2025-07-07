{
  description = "Sequential-Thinking MCP Server";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "sequential-thinking-mcp";
          version = "0.1.0";
          
          src = ./.;
          
          nativeBuildInputs = with pkgs; [
            python
            uv
          ];
          
          buildPhase = ''
            export HOME=$(mktemp -d)
            uv sync --python ${python}/bin/python3
          '';
          
          installPhase = ''
            mkdir -p $out/bin
            cp -r .venv $out/
            
            # Create wrapper script
            cat > $out/bin/sequential-thinking-mcp << EOF
            #!${pkgs.bash}/bin/bash
            exec $out/.venv/bin/sequential-thinking-mcp "\$@"
            EOF
            chmod +x $out/bin/sequential-thinking-mcp
          '';
          
          meta = with pkgs.lib; {
            description = "Sequential-Thinking MCP Server for structured reasoning";
            license = licenses.mit;
            maintainers = [ ];
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            uv
            git
          ];
          
          shellHook = ''
            echo "Sequential-Thinking MCP Server Development Environment"
            echo "Available commands:"
            echo "  uv sync          # Install dependencies"
            echo "  uv run pytest   # Run tests"
            echo "  .venv/bin/sequential-thinking-mcp  # Run server"
          '';
        };
      });
}
