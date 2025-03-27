const nodemailer = require('nodemailer');
const dotenv = require('dotenv');

dotenv.config();

// Create nodemailer transporter with Amazon SES
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'email-smtp.us-east-1.amazonaws.com',
  port: process.env.SMTP_PORT || 587,
  secure: false, // true for 465, false for other ports
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
});

/**
 * Send password reset email with Amazon SES
 * @param {string} email - Recipient email address
 * @param {string} name - Recipient name
 * @param {string} token - Reset token
 */
exports.sendResetPasswordEmail = async (email, name, token) => {
  try {
    // Create the reset password URL
    const resetUrl = `${process.env.FRONTEND_URL || 'http://app.matrizrfm.com.br'}/reset-password?token=${token}`;
    
    // HTML email template
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your Password</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
          }
          .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
          }
          .header {
            background-color: #5E17EB;
            padding: 20px;
            text-align: center;
          }
          .header h1 {
            color: white;
            margin: 0;
          }
          .content {
            padding: 20px;
            background-color: #f9f9f9;
          }
          .button {
            display: inline-block;
            background-color: #5E17EB;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            margin: 20px 0;
          }
          .footer {
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Matriz RFM</h1>
          </div>
          <div class="content">
            <h2>Olá, ${name}</h2>
            <p>Recebemos uma solicitação para redefinir sua senha. Se você não solicitou esta alteração, ignore este email.</p>
            <p>Para redefinir sua senha, clique no botão abaixo:</p>
            <p style="text-align: center;">
              <a href="${resetUrl}" class="button">Redefinir Senha</a>
            </p>
            <p>Ou copie e cole o seguinte link no seu navegador:</p>
            <p>${resetUrl}</p>
            <p>Este link irá expirar em 30 minutos.</p>
          </div>
          <div class="footer">
            <p>&copy; ${new Date().getFullYear()} Matriz RFM. Todos os direitos reservados.</p>
            <p>Este é um email automático, por favor não responda.</p>
          </div>
        </div>
      </body>
      </html>
    `;
    
    // Send email
    await transporter.sendMail({
      from: `"Matriz RFM" <${process.env.EMAIL_FROM || 'no-reply@matrizrfm.com.br'}>`,
      to: email,
      subject: 'Redefinição de Senha - Matriz RFM',
      html: htmlContent
    });
    
    console.log(`Password reset email sent to ${email}`);
    return true;
  } catch (error) {
    console.error('Failed to send password reset email:', error);
    throw error;
  }
}; 