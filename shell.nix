let
  pkgs = import <nixpkgs> {};
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    pyqt6
    pyright
  ]);
in
pkgs.mkShell {
  packages = [
    pythonEnv
  ];
}

