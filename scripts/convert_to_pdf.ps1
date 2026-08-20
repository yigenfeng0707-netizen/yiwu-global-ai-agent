$word = New-Object -ComObject Word.Application
$word.Visible = $false
$files = @("竞品分析", "技术文档", "财务预测与商业计划", "里程碑规划", "风险应对预案", "路演演讲稿", "答辩QA手册", "视频脚本", "部署指南")
foreach ($f in $files) {
    $docx = "D:\YiWuInternetCompetition\$f.docx"
    $pdf = "D:\YiWuInternetCompetition\$f.pdf"
    Write-Host "Converting $f..."
    $doc = $word.Documents.Open($docx)
    $doc.SaveAs([ref]$pdf, [ref]17)
    $doc.Close()
    Write-Host "Done: $f.pdf"
}
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "All PDFs generated"
