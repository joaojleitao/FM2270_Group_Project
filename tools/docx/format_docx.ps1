# Format the pandoc-generated prospectus .docx with Microsoft Word (COM) and export a PDF preview.
# Usage: powershell -ExecutionPolicy Bypass -File tools\docx\format_docx.ps1 <in.docx> <preview.pdf>
param([string]$Path, [string]$PreviewPdf)
$ErrorActionPreference = "Stop"
$blue = 0x794E1F            # Word colours are BGR: RGB #1F4E79
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open((Resolve-Path $Path).Path)

    # --- page: A4, 2 cm margins ---
    $ps = $doc.PageSetup
    $ps.PaperSize = 7                                   # wdPaperA4
    foreach ($m in "TopMargin", "BottomMargin", "LeftMargin", "RightMargin") { $ps.$m = $word.CentimetersToPoints(2) }
    $textWidth = $ps.PageWidth - $ps.LeftMargin - $ps.RightMargin

    # --- styles ---
    $st = $doc.Styles
    foreach ($name in "Normal", "Body Text", "First Paragraph", "Compact") {
        try { $s = $st.Item($name); $s.Font.Name = "Calibri"; $s.Font.Size = 11
              $s.ParagraphFormat.SpaceBefore = 0; $s.ParagraphFormat.SpaceAfter = 5
              $s.ParagraphFormat.LineSpacingRule = 0 } catch {}
    }
    foreach ($pair in @(@("Heading 1", 16), @("Heading 2", 13), @("Heading 3", 11))) {
        $s = $st.Item($pair[0]); $s.Font.Name = "Calibri"; $s.Font.Size = $pair[1]; $s.Font.Bold = $true
        $s.Font.Color = $blue; $s.ParagraphFormat.SpaceBefore = 12; $s.ParagraphFormat.SpaceAfter = 4
        $s.ParagraphFormat.KeepWithNext = $true
    }
    try { $s = $st.Item("Image Caption"); $s.Font.Size = 9; $s.Font.Italic = $false; $s.Font.Color = 0x555555 } catch {}

    # --- cover: everything before the first page break is centred; title larger ---
    $coverEnd = $doc.Content.End
    $find = $doc.Content
    $find.Find.ClearFormatting()
    if ($find.Find.Execute("^m")) { $coverEnd = $find.End }
    $cover = $doc.Range(0, $coverEnd)
    $cover.ParagraphFormat.Alignment = 1                 # centre
    $cover.ParagraphFormat.SpaceAfter = 10
    $cover.Paragraphs.Item(1).Range.Font.Size = 28
    $cover.Paragraphs.Item(1).SpaceBefore = 200

    # --- tables: full width, thin horizontal rules, blue header row, 9 pt ---
    foreach ($t in $doc.Tables) {
        $t.Range.Font.Size = 9
        $t.Range.ParagraphFormat.SpaceAfter = 0
        $t.Borders.Enable = $false
        $t.Borders.Item(-3).LineStyle = 1                # wdBorderHorizontal
        $t.Borders.Item(-1).LineStyle = 1                # top
        $t.Borders.Item(-3).Color = 0xBBBBBB
        $t.Borders.Item(-1).Color = 0xBBBBBB
        $t.Borders.Item(-3).LineWidth = 4                # 0.5 pt
        $t.TopPadding = 1; $t.BottomPadding = 1
        $t.PreferredWidthType = 2; $t.PreferredWidth = 100   # 100% of the text width
        $t.Rows.Item(1).Shading.BackgroundPatternColor = 0xF7F0EA   # RGB #EAF0F7
        $t.Rows.Item(1).Range.Font.Bold = $true
        $t.Rows.Item(1).Range.Font.Color = $blue
        $t.Rows.Item(1).HeadingFormat = $true
        $t.Rows.AllowBreakAcrossPages = $false
    }
    # cover table (first table) has no rules and is left aligned inside the centred block
    if ($doc.Tables.Count -gt 0 -and $doc.Tables.Item(1).Range.Start -lt $coverEnd) {
        $ct = $doc.Tables.Item(1)
        $ct.Borders.Enable = $false
        $ct.Rows.Item(1).Shading.BackgroundPatternColor = -16777216   # automatic (none)
        $ct.Rows.Item(1).Range.Font.Color = 0
        $ct.Range.Font.Size = 11
        $ct.Range.ParagraphFormat.Alignment = 0
        $ct.PreferredWidth = 80
        $ct.Rows.Alignment = 1
    }

    # --- numbers right-aligned (all columns after the first), except text columns of the asset table ---
    for ($k = 2; $k -le $doc.Tables.Count; $k++) {
        $t = $doc.Tables.Item($k)
        $isAssets = $t.Range.Text -like "*Asset class and role*"
        for ($c = 2; $c -le $t.Columns.Count; $c++) {
            if ($isAssets -and $c -eq 2) { continue }
            foreach ($cell in $t.Columns.Item($c).Cells) { $cell.Range.ParagraphFormat.Alignment = 2 }
        }
    }

    # --- centre the weight formula ---
    $r = $doc.Content
    if ($r.Find.Execute("long-only, summing to 100%")) { $r.ParagraphFormat.Alignment = 1 }

    # --- figures: as wide as the text (app screenshot 85%) ---
    $i = 0
    foreach ($s in $doc.InlineShapes) {
        $i++
        $ratio = $s.Height / $s.Width
        $w = if ($i -eq $doc.InlineShapes.Count) { $textWidth * 0.85 } else { $textWidth }
        $s.LockAspectRatio = $true
        $s.Width = $w
        $s.Range.ParagraphFormat.Alignment = 1
    }

    # --- page numbers in the footer (cover page without a number) ---
    $sec = $doc.Sections.Item(1)
    $sec.PageSetup.DifferentFirstPageHeaderFooter = $true
    $null = $sec.Footers.Item(1).PageNumbers.Add(1, $false)   # centred, not on the first page

    $doc.Save()
    if ($PreviewPdf) { $doc.ExportAsFixedFormat($PreviewPdf, 17) }   # wdExportFormatPDF
    "pages: " + $doc.ComputeStatistics(2)
    $doc.Close()
} finally {
    $word.Quit()
}
