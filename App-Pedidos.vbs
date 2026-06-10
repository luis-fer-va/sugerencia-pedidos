' ============================================================================
'  App-Pedidos  ·  Lanzador transparente (sin consola) de la app Streamlit
' ----------------------------------------------------------------------------
'  Doble clic = arranca Streamlit OCULTO y abre Chrome en modo app.
'  Truco "transparente": WScript.Shell.Run(cmd, 0, False) -> 0 = ventana oculta
'  (no se ve ninguna consola negra). Chrome --app=URL abre una ventana limpia,
'  sin pestañas ni barra de direcciones, como si fuera una app de escritorio.
' ============================================================================
Option Explicit

Dim sh, fso, base, pyExe, appPy, port, url, health, i
Set sh  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

base   = fso.GetParentFolderName(WScript.ScriptFullName)
pyExe  = base & "\.venv\Scripts\python.exe"
appPy  = base & "\src\app\app.py"
port   = "8501"
url    = "http://localhost:" & port
health = url & "/_stcore/health"

' 1) Si ya hay una instancia corriendo en el puerto, no la duplicamos.
If Not ServidorArriba(health) Then
    If Not fso.FileExists(pyExe) Then
        MsgBox "No se encontró el entorno virtual:" & vbCrLf & pyExe & vbCrLf & vbCrLf & _
               "Crea el .venv e instala dependencias antes de usar este acceso.", 16, "App-Pedidos"
        WScript.Quit 1
    End If

    sh.CurrentDirectory = base
    ' Lanza Streamlit con la ventana OCULTA (0) y sin esperar (False).
    sh.Run """" & pyExe & """ -m streamlit run """ & appPy & """" & _
           " --server.headless=true --server.port=" & port & _
           " --browser.gatherUsageStats=false", 0, False

    ' 2) Espera (hasta ~40s) a que el servidor responda antes de abrir Chrome.
    For i = 1 To 80
        WScript.Sleep 500
        If ServidorArriba(health) Then Exit For
    Next
End If

' 3) Abre Chrome en modo aplicación (ventana limpia). Fallback: navegador por defecto.
AbrirChrome url


' ---------------------------------------------------------------------------
Function ServidorArriba(u)
    On Error Resume Next
    Dim http
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", u, False
    http.Send
    ServidorArriba = (Err.Number = 0 And http.Status = 200)
    On Error GoTo 0
End Function

Sub AbrirChrome(u)
    Dim rutas, p, chrome
    chrome = ""
    rutas = Array( _
        sh.ExpandEnvironmentStrings("%ProgramFiles%")      & "\Google\Chrome\Application\chrome.exe", _
        sh.ExpandEnvironmentStrings("%ProgramFiles(x86)%") & "\Google\Chrome\Application\chrome.exe", _
        sh.ExpandEnvironmentStrings("%LocalAppData%")      & "\Google\Chrome\Application\chrome.exe")
    For Each p In rutas
        If fso.FileExists(p) Then
            chrome = p
            Exit For
        End If
    Next

    If chrome <> "" Then
        sh.Run """" & chrome & """ --app=" & u, 1, False
    Else
        ' Sin Chrome: abre en el navegador por defecto.
        sh.Run u, 1, False
    End If
End Sub
