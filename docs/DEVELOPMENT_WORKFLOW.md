# 🚀 Team Development Workflow (Production-like)

## 🧠 1. Branch Strategy

| Branch | Purpose |
|--------|--------|
| main | Production (stable, không code trực tiếp) |
| develop | Integration (tổng hợp feature) |
| feature/* | Dev làm task riêng |
| fix/* | Fix bug |
| hotfix/* | Fix khẩn cấp |

👉 Nguyên tắc:
- ❌ Không commit trực tiếp vào `main` hoặc `develop`
- ✅ Mọi thứ phải qua Pull Request (PR)

---

## 🔄 2. Daily Workflow (Mỗi Dev)

### 🌅 Bước 1 — Update code mới nhất

```bash
git checkout develop
git pull origin develop
```

---

### 🌱 Bước 2 — Tạo branch cho task

```bash
git checkout -b feature/<task-name>
```

**Ví dụ:**
```bash
git checkout -b feature/data-preprocessing
```

---

### 💻 Bước 3 — Code & Commit

👉 Quy tắc:
- Commit nhỏ, rõ ràng
- Không commit code lỗi

**Ví dụ:**
```bash
git add .
git commit -m "feat: add data cleaning module"
git commit -m "feat: handle missing values"
git commit -m "refactor: optimize preprocessing pipeline"
```

---

### 🚀 Bước 4 — Push code

```bash
git push origin feature/<task-name>
```

---

## 🔀 3. Pull Request (PR) Workflow

### 🧩 Bước 1 — Tạo PR

- Base: `develop`
- Compare: `feature/<task-name>`

---

### ✍️ Bước 2 — Viết mô tả PR

**Template:**

```text
Title:
[Feature] Data preprocessing pipeline

Description:

## What does this PR do?
- Implement data cleaning
- Handle missing values
- Normalize dataset

## Related Issue
#12

## How to test?
- Run preprocessing script
- Check output dataset

## Checklist
- [x] Code runs successfully
- [x] No conflict
- [x] Follow coding convention
```

---

### 👀 Bước 3 — Assign Reviewer

- Ít nhất 1 người review
- ❌ Không self-review

---

### 🔍 Bước 4 — Code Review

Reviewer kiểm tra:

- Logic đúng không
- Có bug không
- Code clean không
- Có tối ưu không (đặc biệt Data/AI)

**Ví dụ comment:**
```text
- Nên xử lý thêm case null
- Function này nên tách ra
- Có thể dùng vectorization thay vì loop
```

---

### 🔁 Bước 5 — Fix theo review

```bash
git add .
git commit -m "fix: handle edge case null values"
git push
```

---

### ✅ Bước 6 — Merge PR

Điều kiện:
- ✔️ Pass review
- ✔️ Không conflict

→ Merge vào `develop`

---

## 🔄 4. Sau khi merge

```bash
git checkout develop
git pull origin develop
```

Xóa branch:

```bash
git branch -d feature/<task-name>
```

---

## ⚔️ 5. Xử lý conflict

```bash
git checkout feature/<task>
git pull origin develop
```

👉 Fix conflict → commit → push lại

---

## 📦 6. Example Workflow (Full)

### Scenario:
Task: Train model Logistic Regression

---

### B1:
```bash
git checkout develop
git pull
git checkout -b feature/train-model
```

---

### B2:
```bash
git commit -m "feat: add logistic regression model"
```

---

### B3:
```bash
git push origin feature/train-model
```

---

### B4:
Tạo PR:
```
feature/train-model → develop
```

---

### B5:
Reviewer comment:
```
Nên normalize data trước khi train
```

---

### B6:
```bash
git commit -m "fix: add data normalization"
git push
```

---

### B7:
PR approved → merge

---

## 📅 7. Daily Team Workflow

Mỗi ngày:

1. Pull `develop`
2. Code task riêng
3. Push branch
4. Tạo PR
5. Review chéo
6. Merge

---

## 🚫 8. Common Mistakes

- ❌ Code trực tiếp vào `develop` hoặc `main`
- ❌ Không pull trước khi code
- ❌ PR không có mô tả
- ❌ Không review code
- ❌ Commit kiểu: "fix bug"

---

## 🧠 9. Best Practices

### ✔️ Commit Convention

| Type | Meaning |
|------|--------|
| feat | Feature mới |
| fix | Bug fix |
| refactor | Cải tiến code |
| docs | Documentation |
| chore | Config / setup |

---

### ✔️ PR nhỏ & rõ ràng
- Không nên > 500 dòng code

---

### ✔️ Review nhanh
- Không để PR quá lâu

---

### ✔️ Luôn test trước khi PR

---

## ⚡ 10. Core Principles

- Không code vào `main`
- Mọi thứ qua PR
- Review là bắt buộc
- Luôn pull trước khi code

---

## 🏁 Final Workflow

```
develop → feature → PR → review → merge → develop
```

