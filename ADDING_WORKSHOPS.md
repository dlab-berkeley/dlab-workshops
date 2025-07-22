# Adding New Workshops to D-Lab Website

This guide explains how to add new workshops to the D-Lab workshops website after the Jekyll templating system has been implemented.

## Quick Start

To add a new workshop, you only need to edit **one file**: `_data/workshops.yml`

## Step-by-Step Instructions

### 1. Open the workshops data file
Edit the file `_data/workshops.yml` in your favorite text editor.

### 2. Add your workshop entry
Add a new entry following this template:

```yaml
- title: "Your Workshop Title"
  category: "python"  # or "r" or "other"
  level: "introductory"  # or "intermediate" or "advanced"
  github_url: "https://github.com/dlab-berkeley/Your-Workshop-Repo"
  description: "A clear, concise description of what the workshop covers."
  prerequisites: ["Workshop 1", "Workshop 2"]  # or [] for none
  datahub_url: "https://datahub.berkeley.edu/hub/user-redirect/git-pull?repo=..."  # optional
  binder_url: "https://mybinder.org/v2/gh/dlab-berkeley/Your-Workshop-Repo/main"  # optional
  slides_url: "https://your-slides-url.com"  # optional
```

### 3. Required Fields
- `title`: The workshop name (e.g., "Python Data Visualization")
- `category`: Must be one of: `"python"`, `"r"`, or `"other"`
- `level`: Must be one of: `"introductory"`, `"intermediate"`, or `"advanced"`
- `github_url`: Link to the workshop's GitHub repository
- `description`: Brief description of the workshop content
- `prerequisites`: Array of prerequisite workshop names (use `[]` if none)

### 4. Optional Fields
- `datahub_url`: Direct link to launch workshop on UC Berkeley Datahub
- `binder_url`: Link to launch workshop on Binder
- `slides_url`: Link to workshop slides or presentation
- `parts`: For multi-part workshops (see example below)

### 5. Multi-part Workshop Example
```yaml
- title: "Python Fundamentals"
  category: "python"
  level: "introductory"
  github_url: "https://github.com/dlab-berkeley/Python-Fundamentals"
  description: "Learn the basics of Python programming."
  prerequisites: []
  parts:
    - name: "Part 1-3"
      focus: "Data types, variables, and control structures"
    - name: "Part 4-6"
      focus: "Functions, packages, and file I/O"
```

## Workshop Categories

### Python Workshops (`category: "python"`)
- Appear on the Python page (`python.html`)
- Use blue color scheme
- Include data science and programming workshops

### R Workshops (`category: "r"`)
- Appear on the R page (`R.html`)  
- Use yellow/orange color scheme
- Include statistical analysis workshops

### Other Workshops (`category: "other"`)
- Appear on the Other page (`other.html`)
- Use green color scheme
- Include Git, SQL, Julia, and specialized tools

## Workshop Levels

- **Introductory** (green badge): No prior experience needed
- **Intermediate** (yellow badge): Some prior experience recommended  
- **Advanced** (red badge): Significant prior experience required

## After Adding a Workshop

1. **Commit your changes** to Git
2. **Push to GitHub** - the site will automatically rebuild
3. **Check the website** to ensure your workshop appears correctly
4. **Verify all links work** (GitHub, Datahub, Binder, etc.)

## Best Practices

1. **Consistent Naming**: Follow the pattern "Language/Tool + Topic" (e.g., "Python Web Scraping", "R Data Visualization")
2. **Clear Descriptions**: Write 1-2 sentences describing what students will learn
3. **Prerequisites**: List actual workshop names that appear elsewhere in the data file
4. **URLs**: Test all URLs to ensure they work correctly
5. **Alphabetical Order**: Consider adding workshops in alphabetical order within each category

## Examples

### Basic Workshop
```yaml
- title: "SQL Fundamentals"
  category: "other"
  level: "introductory"
  github_url: "https://github.com/dlab-berkeley/SQL-Fundamentals"
  description: "Query and manage relational databases using SQL."
  prerequisites: []
```

### Workshop with Prerequisites and Multiple Links
```yaml
- title: "Python Machine Learning"
  category: "python"
  level: "advanced"
  github_url: "https://github.com/dlab-berkeley/Python-Machine-Learning"
  description: "Introduction to machine learning algorithms using scikit-learn."
  prerequisites: ["Python Fundamentals", "Python Data Wrangling", "Python Data Visualization"]
  datahub_url: "https://datahub.berkeley.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fdlab-berkeley%2FPython-Machine-Learning&urlpath=tree%2FPython-Machine-Learning%2F"
  binder_url: "https://mybinder.org/v2/gh/dlab-berkeley/Python-Machine-Learning/main"
```

## Troubleshooting

- **Workshop not appearing**: Check YAML syntax and indentation
- **Wrong page**: Verify the `category` field is correct
- **Wrong color**: Check that `level` is spelled correctly
- **Links not working**: Test URLs in a browser before adding

## Questions?

If you need help or have questions about adding workshops, please:
1. Check this documentation first
2. Look at existing workshop entries in `_data/workshops.yml` for examples
3. Create an issue in the repository with your question