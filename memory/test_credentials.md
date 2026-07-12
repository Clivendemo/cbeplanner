# Test Credentials

## Test Teacher Account (Primary)
- Email: visualtest2026@example.com
- Password: Visual@2026
- Role: teacher
- Note: Created fresh 2026-02-12 for E2E visual layout testing.

## Legacy Test Teacher Account (may be invalid)
- Email: testteacher2026@gmail.com
- Password: TestPass123!
- Role: teacher
- Note: Returned INVALID_LOGIN_CREDENTIALS as of 2026-02-12 — use `visualtest2026@example.com` above.

## Admin Account (Primary)
- Email: mail2clive@gmail.com
- Password: (user's existing Firebase password)
- Role: admin

## Admin Account (Test)
- Email: testadmin2026@gmail.com
- Password: AdminTest123!
- Role: admin

## Firebase API Key
- AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8

## URLs
- Backend: https://magical-shannon-6.preview.emergentagent.com
- Frontend: https://magical-shannon-6.preview.emergentagent.com

## Getting Firebase ID Token (for API testing)
POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8
Body: {"email":"visualtest2026@example.com","password":"Visual@2026","returnSecureToken":true}
Use: Authorization: Bearer {idToken}

## Creating fresh Firebase test accounts (curl)
POST https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8
Body: {"email":"anytest@example.com","password":"YourPassword!","returnSecureToken":true}
