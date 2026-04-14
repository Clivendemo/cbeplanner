# Test Credentials

## Test Teacher Account
- Email: testteacher2026@gmail.com
- Password: TestPass123!
- Role: teacher

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
Body: {"email":"testteacher2026@gmail.com","password":"TestPass123!","returnSecureToken":true}
Use: Authorization: Bearer {idToken}
