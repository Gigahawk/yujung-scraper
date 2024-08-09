{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv defaultPoetryOverrides;
      poetryEnv = mkPoetryEnv {
        projectDir = ./.;
      };
      myPython = pkgs.python3;
      pythonWithPackages = myPython.withPackages (p: with p; [
        playwright
      ]);
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          #poetryEnv
          pythonWithPackages
          pkgs.playwright-driver.browsers
        ];
        shellHook = ''
          export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
          export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
          ##export PWDEBUG=1
        '';
      };
      devShells.poetry = pkgs.mkShell {
        buildInputs = [
          # Required to make poetry shell work properly
          pkgs.bashInteractive
        ];
        packages = [
          pkgs.poetry
        ];
      };
    });
}