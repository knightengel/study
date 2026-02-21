let
  pkgs = import <nixpkgs> {};
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    pyqt6
    # Если нужны еще пакеты, добавляйте их сюда, например: requests, numpy
  ]);
in
pkgs.mkShell {
  packages = [
    pythonEnv
  ];
}

