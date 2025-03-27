const jwt = require('jsonwebtoken');
const { User, ResetToken } = require('../models');
const { sendResetPasswordEmail } = require('../utils/emailService');
const { v4: uuidv4 } = require('uuid');

// Register a new user
exports.register = async (req, res) => {
  try {
    const { name, email, password } = req.body;
    
    // Check if user already exists
    const existingUser = await User.findOne({ where: { email } });
    if (existingUser) {
      return res.status(400).json({ success: false, message: 'Email already in use' });
    }
    
    // Create new user
    const user = await User.create({
      name,
      email,
      password
    });
    
    // Create JWT token
    const token = jwt.sign(
      { id: user.id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    // Return success with token
    return res.status(201).json({
      success: true,
      message: 'User registered successfully',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Register error:', error);
    return res.status(500).json({ success: false, message: 'Registration failed' });
  }
};

// Login user
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user by email
    const user = await User.findOne({ where: { email } });
    if (!user) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    
    // Check password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    
    // Create JWT token
    const token = jwt.sign(
      { id: user.id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    // Return success with token
    return res.status(200).json({
      success: true,
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ success: false, message: 'Login failed' });
  }
};

// Forgot password
exports.forgotPassword = async (req, res) => {
  try {
    const { email } = req.body;
    
    // Find user by email
    const user = await User.findOne({ where: { email } });
    if (!user) {
      // For security reasons, still return success even if email doesn't exist
      return res.status(200).json({ success: true, message: 'Password reset email sent' });
    }
    
    // Generate a unique reset token
    const token = uuidv4();
    
    // Set token expiration (30 minutes)
    const expiresAt = new Date();
    expiresAt.setMinutes(expiresAt.getMinutes() + 30);
    
    // Delete any existing tokens for this user
    await ResetToken.destroy({ where: { user_id: user.id } });
    
    // Create new reset token
    await ResetToken.create({
      user_id: user.id,
      token,
      expires_at: expiresAt
    });
    
    // Send reset password email
    await sendResetPasswordEmail(user.email, user.name, token);
    
    return res.status(200).json({ success: true, message: 'Password reset email sent' });
  } catch (error) {
    console.error('Forgot password error:', error);
    return res.status(500).json({ success: false, message: 'Failed to send reset email' });
  }
};

// Reset password
exports.resetPassword = async (req, res) => {
  try {
    const { token, password } = req.body;
    
    // Find the token in the database
    const resetToken = await ResetToken.findOne({ where: { token } });
    if (!resetToken) {
      return res.status(400).json({ success: false, message: 'Invalid or expired token' });
    }
    
    // Check if token is expired
    if (new Date() > new Date(resetToken.expires_at)) {
      // Delete expired token
      await resetToken.destroy();
      return res.status(400).json({ success: false, message: 'Token has expired' });
    }
    
    // Find the user
    const user = await User.findByPk(resetToken.user_id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    // Update user's password
    user.password = password;
    await user.save();
    
    // Delete the used token
    await resetToken.destroy();
    
    return res.status(200).json({ success: true, message: 'Password reset successful' });
  } catch (error) {
    console.error('Reset password error:', error);
    return res.status(500).json({ success: false, message: 'Failed to reset password' });
  }
};

// Verify token
exports.verifyToken = async (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(401).json({ success: false, message: 'No token provided' });
    }
    
    // Verify the token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Find the user
    const user = await User.findByPk(decoded.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    return res.status(200).json({
      success: true,
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Verify token error:', error);
    return res.status(401).json({ success: false, message: 'Invalid token' });
  }
}; 