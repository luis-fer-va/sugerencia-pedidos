' ============================================================================
'  Crea un acceso directo "App-Pedidos" en el Escritorio que abre la app
'  de forma transparente (sin consola). Ejecútalo UNA vez (doble clic).
' ============================================================================
Option Explicit

Dim sh, fso, base, desktop, lnkPath, lnk, pngPath, icoPath, pyExe

Set sh  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

base    = fso.GetParentFolderName(WScript.ScriptFullName)
desktop = sh.SpecialFolders("Desktop")
lnkPath = desktop & "\App-Pedidos.lnk"
pngPath = base & "\src\app\assets\logo_laroka.png"
icoPath = base & "\src\app\assets\logo_laroka.ico"
pyExe   = base & "\.venv\Scripts\python.exe"

' 1) Si hay logo .png pero no .ico, genera el .ico con Pillow (para el ícono del acceso).
If fso.FileExists(pngPath) And (Not fso.FileExists(icoPath)) And fso.FileExists(pyExe) Then
    Dim code
    code = "from PIL import Image; Image.open(r'" & pngPath & "').save(r'" & icoPath & _
           "', sizes=[(16,16),(32,32),(48,48),(256,256)])"
    sh.Run """" & pyExe & """ -c """ & code & """", 0, True
End If

' 2) Crea el acceso directo apuntando a wscript + el lanzador (así NO aparece consola).
Set lnk = sh.CreateShortcut(lnkPath)
lnk.TargetPath       = "wscript.exe"
lnk.Arguments        = """" & base & "\App-Pedidos.vbs"""
lnk.WorkingDirectory = base
lnk.Description       = "Abrir la App de Toma de Pedidos (La Roka)"
If fso.FileExists(icoPath) Then
    lnk.IconLocation = icoPath
End If
lnk.Save

MsgBox "Listo. Se creó el acceso directo 'App-Pedidos' en el Escritorio." & vbCrLf & _
       "Doble clic en él para abrir la app en Chrome.", 64, "La Roka"
