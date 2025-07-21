# Quick Reference: App Builder Parameters

Copy and paste these parameter strings into the Code Ocean App Builder text box:

## 🧠 Common Brain Regions

### Locus Coeruleus (LC)
```
--soma-location LC
```

### Substantia Innominata (SI)
```
--soma-location SI
```

### Reticular Thalamus (RT)
```
--soma-location RT
```

### Paraventricular Thalamus (PVT)
```
--soma-location PVT
```

### Ventromedial (VM)
```
--soma-location VM
```

### Medulla
```
--soma-location medulla
```

## 🔍 HIVE-Filtered Analysis

### LC with HIVE Filter
```
--soma-location LC --hive-filter
```

### SI with HIVE Filter
```
--soma-location SI --hive-filter
```

### All Neurons with HIVE Filter
```
--soma-location all --hive-filter
```

## 📊 Different Output Formats

### PNG Plots
```
--soma-location LC --plot-format png
```

### Interactive HTML Plots
```
--soma-location SI --hive-filter --plot-format html
```

### SVG Vector Graphics (default)
```
--soma-location RT --plot-format svg
```

## 🌍 Comprehensive Analysis

### All Neurons (No Location Filter)
```
--soma-location all
```

### All Neurons with HIVE Filter + PNG Output
```
--soma-location all --hive-filter --plot-format png
```

## ⚙️ Advanced Options

### Skip CSV Export (Plots Only)
```
--soma-location LC --no-csv
```

### Skip Plots (CSV Only)
```
--soma-location SI --hive-filter --no-plots
```

### Minimal Output (No Files, Console Only)
```
--soma-location RT --no-csv --no-plots
```

---

**Need Help?** 
- Use `--help` to see all available options
- Check the README.md for detailed explanations
- Default format is SVG, default includes both CSV and plots 