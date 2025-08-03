# Better Questions

Better Questions is a free, open-source tool that helps patients and caregivers generate research-backed questions to ask their doctors. It searches PubMed in real time and uses GPT to suggest medically relevant, citation-supported inquiries based on symptoms and known conditions.

> ⚠️ This tool does not provide medical advice or diagnoses. All results are generated from public literature. Always consult a licensed physician.

---

## 🌐 Live Demo

You can try the live version at:  
**[https://bq.bettertoolsfromcharles.com](https://bq.bettertoolsfromcharles.com)**

The code in this repository powers that tool and is manually synced.

---

## ✨ Features

- Real-time PubMed integration using NCBI E-Utilities
- GPT-powered question framing with strict citation enforcement
- Recursive subset search for broader coverage
- Article scoring by relevance, recency, novelty, and actionability
- Copy-paste friendly output and plaintext export
- Transparent token logging (locally only)
- No ads, tracking, or affiliate manipulation

---

## 🛠️ How It Works

1. User enters up to 3 symptoms and 3 known conditions.
2. PubMed is queried for all valid subset combinations.
3. Articles are scored using the `article_scorer.py` system.
4. The top articles are passed to GPT to frame medically relevant questions.
5. Only citation-backed questions are returned, with clickable PubMed links.

---

## 🧾 License & Ethics

This project is released under the **AGPL-3.0** license.  
See `LICENSE.md` for the full text and ethical clause.

The tool is free to use and free to improve — but any public forks or modified deployments must:

- Preserve user privacy (no hidden logging or tracking)
- Disclose all changes clearly
- Keep the citation-only logic intact unless improved transparently

---

## 🙌 Support the Project

This tool is free, but not free to maintain.

If it helped you or someone you love, consider donating:

- [PayPal Donation Link](https://www.paypal.com/donate/?hosted_button_id=JGAJ3QFCCKNNN)
- [GoFundMe Campaign](https://www.gofundme.com/f/better-questions)

Every dollar helps offset API costs and fund continued development.

---

## 🧠 Why This Matters

Diagnosing complex conditions is hard — especially when symptoms are vague or overlap with other issues.  
Better Questions is designed to help patients **ask better-informed questions earlier**, using public research, not speculation.

---

## 🤝 Contributing

Pull requests and forks are welcome. This repo is not directly tied to the production site, so feel free to experiment.

For major changes, please open an issue first to discuss the scope or intent.

