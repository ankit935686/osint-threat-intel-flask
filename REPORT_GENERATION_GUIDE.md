# PDF Report Generation Guide

## 📄 Project Report Generator for OSINT Threat Intelligence Pipeline

### Team Members:
- **Ankit Satpute** (10218)
- **Nick Pereira** (10214)
- **Piyush Pawar** (10213)

---

## 🚀 Quick Start

### Generate Basic Report (Without Screenshots)

```powershell
python generate_project_report.py
```

This will create: **`Project_Report_OSINT_Threat_Intelligence.pdf`**

---

## 📸 Adding Dashboard Screenshots

### Step 1: Prepare Your Screenshots

1. Take screenshots of your dashboard showing:
   - Main dashboard overview
   - Risk distribution charts
   - Source attribution visualizations
   - High-risk threats table
   - Correlation graph
   - Geographic distribution

2. Save them as PNG or JPG files with descriptive names:
   - `dashboard_overview.png`
   - `risk_distribution.png`
   - `threat_by_source.png`
   - `correlation_graph.png`
   - `geographic_distribution.png`
   - etc.

### Step 2: Create Screenshots Folder

```powershell
# Create screenshots folder in project root
mkdir screenshots
```

### Step 3: Add Your Images

Copy all your dashboard screenshot images into the `screenshots` folder.

### Step 4: Generate Report with Screenshots

```powershell
python add_screenshots_to_report.py
```

This will create: **`Project_Report_OSINT_With_Screenshots.pdf`**

---

## 📋 What's Included in the Report

### ✅ Your Team Information
- Ankit Satpute (10218)
- Nick Pereira (10214)
- Piyush Pawar (10213)

### ✅ Your API Configuration
The report includes all the API keys you've configured:
- **AlienVault OTX**: 162b027948128a1d56...
- **VirusTotal**: dfefdca31c1a686497...
- **GreyNoise**: 92bd0280-c602-4b1a-bffb-df7c429e52b9
- **Shodan**: oB2F1R5FP8My2KHrkP9uN1gBHUaMYiKA
- **AbuseIPDB**: 38a722115cdbaa88f1...
- **IPInfo**: 7ca7a4213e1157

### ✅ Complete Documentation
1. **Abstract** - Project overview and objectives
2. **System Architecture** - Data flow and design
3. **Source Selection** - All 7 OSINT sources used
4. **Module Documentation**:
   - Module 3: Collection
   - Module 4: Normalization
   - Module 5: Enrichment
   - Module 6: Merge & Deduplication
   - Module 7: Graph Correlation
   - Module 8: Scoring & Prioritization
   - Module 10: Reporting & Visualization
   - Module 11 & 12: Orchestration & Validation
5. **Dashboard Showcase** - Description and screenshots
6. **Technology Stack** - Python, Flask, Pandas, NetworkX, etc.
7. **Conclusion** - Key achievements and future work

---

## 🎨 Tips for Best Results

### Screenshot Quality
- Use high-resolution screenshots (1920x1080 or higher)
- Capture full dashboard views
- Ensure text is readable in screenshots
- Use consistent browser zoom level (100%)

### Screenshot Organization
Name your files in order you want them to appear:
```
01_main_dashboard.png
02_risk_charts.png
03_source_distribution.png
04_correlation_graph.png
05_threat_table.png
```

### File Formats
- Supported: PNG, JPG, JPEG
- Recommended: PNG (better quality for UI screenshots)
- Max file size: Keep images under 5MB each

---

## 🔧 Troubleshooting

### "reportlab not found"
```powershell
pip install reportlab
```

### "No images found in screenshots folder"
- Make sure images are directly in the `screenshots` folder
- Check file extensions (must be .png, .jpg, or .jpeg)
- Verify filenames don't have special characters

### Images too large in PDF
- The script automatically resizes images to fit the page
- For manual control, resize images to 1920x1080 before adding

### PDF generation fails
- Check that all required files exist
- Ensure you have write permissions in the directory
- Try running from the project root directory

---

## 📦 Required Dependencies

```txt
reportlab>=3.6.0
```

Install with:
```powershell
pip install reportlab
```

---

## 📝 Report Customization

If you need to modify the report content:

1. Open `generate_project_report.py`
2. Modify the relevant section methods:
   - `create_abstract()` - Change abstract text
   - `create_system_architecture()` - Update architecture description
   - `create_module_*()` - Modify module descriptions
   - `create_conclusion()` - Update conclusion

3. Regenerate the report:
   ```powershell
   python generate_project_report.py
   ```

---

## ✨ Output Files

After running the scripts, you'll have:

1. **`Project_Report_OSINT_Threat_Intelligence.pdf`**
   - Basic report without screenshots
   - ~150-200 KB file size
   - Quick to generate

2. **`Project_Report_OSINT_With_Screenshots.pdf`** (if screenshots added)
   - Complete report with dashboard images
   - Larger file size (depends on number/size of images)
   - Final submission version

---

## 🎓 Academic Submission

For your final submission, use:
**`Project_Report_OSINT_With_Screenshots.pdf`**

This includes:
- ✅ All team member details
- ✅ Complete technical documentation
- ✅ Your actual API configuration
- ✅ Dashboard screenshots demonstrating the working system
- ✅ Professional formatting suitable for academic submission

---

## 📞 Need Help?

If you encounter any issues:
1. Check that you're in the correct directory
2. Verify all dependencies are installed
3. Ensure screenshot files are in the correct folder
4. Try running with Python 3.8 or higher

---

**Generated for:** TE COMPS A - Experiment 8  
**College:** Fr. Conceicao Rodrigues College of Engineering  
**Department:** Computer Engineering
