import apiService from './apiService';

class SmsService {
  // Send verification code
  async sendVerificationCode(phoneNumber) {
    return await apiService.post('/sms/send-verification', {
      phone_number: phoneNumber
    });
  }
  
  // Verify code
  async verifyCode(phoneNumber, code) {
    return await apiService.post('/sms/verify-code', {
      phone_number: phoneNumber,
      verification_code: code
    });
  }
  
  // Get verification status
  async getVerificationStatus(phoneNumber) {
    return await apiService.get('/sms/status', {
      phone_number: phoneNumber
    });
  }
}

const smsServiceInstance = new SmsService();
export default smsServiceInstance;