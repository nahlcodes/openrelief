# openrelief
An open-source tool for smarter, more transparent donation and resource allocation.

# 🌍 OpenRelief

### Every resource. The right place. Less left unmet.

OpenRelief is an open-source resource allocation planning tool designed to help community initiatives, schools, charities, and relief organisations distribute limited resources more transparently.

Whether a team is distributing books, stationery, winter clothing, or other essential supplies, OpenRelief helps turn available stock and recorded needs into an allocation plan.

## 💡 Why OpenRelief?

Community drives often work with limited supplies and many different needs. Planning distributions can be difficult when information is scattered or resources are insufficient.

OpenRelief aims to make that process easier by helping organisers:

- Record available donations and recipient needs.
- Compare shortages against available stock.
- Explore need-based and equal-distribution strategies.
- Set recipient capacity limits.
- Identify unmet needs and leftover resources.
- Download allocation results as a CSV report.

## ✨ Features

- **Flexible resources:** Use your own resource names.
- **Need-based allocation:** Consider recorded priority levels.
- **Equal distribution:** Allocate available units in rounds.
- **Capacity limits:** Avoid allocating more than a recipient can receive.
- **Transparent results:** Review allocations, remaining shortages, and leftovers.
- **CSV export:** Download results for further review.

## 🚀 Try OpenRelief

OpenRelief runs as a web application built with Streamlit.

To run it locally:

1. Install Python.
2. Clone this repository.
3. Install the required packages.
4. Start the application.

```bash
git clone https://github.com/nahlcodes/openrelief.git
cd openrelief
pip install -r requirements.txt
streamlit run app.py
```

Replace `YOUR-USERNAME` with your GitHub username.

## 🛠️ Technology

- Python
- Streamlit
- Pandas

## 🧭 How it works

1. Enter available resources and quantities.
2. Record recipient needs, existing stock, priorities, and capacity limits.
3. Select an allocation strategy.
4. Generate and review the proposed allocation.
5. Use the results to support human decision-making.

## ⚖️ Important limitations

OpenRelief is an allocation planning tool, not an automated authority on who deserves assistance.

Its results depend on the information entered and the assumptions of the selected strategy. Priority ratings should be based on transparent, reviewed criteria. Organisers must verify their data and assess the fairness and suitability of every recommendation before distributing resources.

The current prototype matches resources using their names. It does not yet understand all differences in size, suitability, quality, or recipient-specific requirements.

Do not enter identifiable or sensitive personal information about recipients into the public demo.

## 🌱 Contributing

Contributions, bug reports, testing, documentation improvements, and new ideas are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing.

## 📄 Licence

OpenRelief is released under the MIT License. See [LICENSE](LICENSE) for details.
