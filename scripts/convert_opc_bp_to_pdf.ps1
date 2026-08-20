$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\YiWuInternetCompetition\OPC赛道商业计划书.docx")
$pdf = "D:\YiWuInternetCompetition\OPC赛道商业计划书.pdf"
$doc.SaveAs([ref]$pdf, [ref]17)
$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "PDF Done"
