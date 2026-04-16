# 금융감독원 비조치의견서·법령해석 이메일 알림

금융감독원 사이트에서 **비조치의견서**와 **법령해석** 신규 게시글을 감지하여  
매일 **오전 7시, 오후 3시 (KST)** 에 이메일로 발송합니다.

---

## 1. GitHub Repository Secrets 등록

`Settings → Secrets and variables → Actions → New repository secret`에서  
아래 3개의 시크릿을 등록하세요.

| Secret 이름 | 설명 | 예시 |
|---|---|---|
| `FSS_EMAIL_SENDER` | 발신 Gmail 주소 | `yourname@gmail.com` |
| `FSS_EMAIL_PASSWORD` | Gmail **앱 비밀번호** (16자리) | `abcd efgh ijkl mnop` |
| `FSS_EMAIL_RECIPIENTS` | 수신자 이메일 (쉼표로 여러 명 가능) | `a@gmail.com,b@company.com` |

> **Gmail 앱 비밀번호 발급 방법**  
> 1. Google 계정 → [보안](https://myaccount.google.com/security)  
> 2. **2단계 인증** 활성화 (필수)  
> 3. [앱 비밀번호](https://myaccount.google.com/apppasswords) 페이지에서 앱 이름 입력 후 생성  
> 4. 생성된 16자리 비밀번호를 `FSS_EMAIL_PASSWORD`에 입력

---

## 2. 수신자 추가/변경

`FSS_EMAIL_RECIPIENTS` 시크릿 값을 수정하면 됩니다.  
쉼표로 구분하여 여러 명 지정 가능:

```
a@gmail.com, b@company.com, c@example.com
```

---

## 3. 수동 실행 (테스트)

GitHub Actions 탭 → `FSS 비조치의견서·법령해석 알림` → **Run workflow**

---

## 4. 실행 시각

| 발송 시각 (KST) | cron (UTC) |
|---|---|
| 오전 07:00 | `0 22 * * *` (전날 22:00 UTC) |
| 오후 15:00 | `0 6 * * *` |

---

## 5. 동작 방식

1. FSS 사이트 비조치의견서·법령해석 목록 페이지 스크래핑
2. `seen_items.json`에 없는 신규 항목만 필터링
3. HTML 이메일로 발송
4. 발송된 항목 ID를 `seen_items.json`에 기록 후 자동 커밋 (중복 방지)
