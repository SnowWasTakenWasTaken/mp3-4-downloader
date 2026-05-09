OutFile "YouTubeDownloaderSetup.exe"
InstallDir "$PROGRAMFILES\YouTube Downloader"

Page directory
Page instfiles

Section

  SetOutPath $INSTDIR

  File "C:\\Users\\alex2\\dist\\youtube_downloader.exe"

  CreateShortcut "$DESKTOP\YouTube Downloader.lnk" "$INSTDIR\youtube_downloader.exe"

  CreateDirectory "$SMPROGRAMS\YouTube Downloader"
  CreateShortcut "$SMPROGRAMS\YouTube Downloader\YouTube Downloader.lnk" "$INSTDIR\youtube_downloader.exe"

SectionEnd
