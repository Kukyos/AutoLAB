"""Launch the AutoLAB desktop app. PyInstaller's entry point (see AutoLAB.spec).

Installed users run `autolab app` instead.
"""

from autolab.desktop import main

raise SystemExit(main())
