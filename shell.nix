{ pkgs ? import <nixpkgs> {
    overlays = [
      (self: super: {
        opencv4 = super.opencv4.override {
          enableGtk2 = true;
          enableGtk3 = true;
          enablePython = true;
        };
      })
    ];
  }
}:

let
  pythonWithPackages = pkgs.python3.withPackages (python: [
    python.opencv4 # We've overlayed opencv4
    python.numpy
    python.pandas
    python.requests
    python.google-genai
    # python.keras
  ]);
  buildInputAlias = [
    pythonWithPackages
    pkgs.python3Packages.pip
    pkgs.scrot
    pkgs.wmctrl
    pkgs.xorg.xwininfo
  ];
in
pkgs.stdenv.mkDerivation {
  name = "bullshit";
  buildInputs = buildInputAlias;

  shellHook = ''
    # source venv/bin/activate
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath buildInputAlias}:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib/:$LD_LIBRARY_PATH"
    export PATH="${pythonWithPackages}/bin:$PATH"
  '';
}
