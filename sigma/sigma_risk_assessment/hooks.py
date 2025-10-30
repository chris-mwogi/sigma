app_name = "sigma"
app_title = "Sigma"
app_publisher = "Prismod Technologies Limited"
app_description = "Sigma suite: Risk Assessment module"
app_icon = "octicon octicon-alert"
app_color = "red"
app_email = "dev@prismod.co.ke"
app_license = "MIT"

app_include_js = ["/assets/sigma/js/risk_assessment_dashboard.js"]

fixtures = [
    {
        "dt": "Property Setter",
        "filters": [["name", "in", ["Risk Assessment-status-read_only", "Risk Assessment-risk_score-read_only"]]]
    }
]
