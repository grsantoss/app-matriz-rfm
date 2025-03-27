const { Sequelize } = require('sequelize');
const dotenv = require('dotenv');

dotenv.config();

// Database configuration
const sequelize = new Sequelize(
  process.env.DB_NAME || 'rfmmatrix',
  process.env.DB_USER || 'rfmuser',
  process.env.DB_PASSWORD,
  {
    host: process.env.DB_HOST || 'db',
    dialect: 'postgres',
    port: process.env.DB_PORT || 5432,
    logging: false,
    pool: {
      max: 5,
      min: 0,
      acquire: 30000,
      idle: 10000
    }
  }
);

// Import models
const User = require('./User')(sequelize);
const ResetToken = require('./ResetToken')(sequelize);

// Setup associations
User.hasMany(ResetToken, { foreignKey: 'user_id' });
ResetToken.belongsTo(User, { foreignKey: 'user_id' });

// Export models and sequelize instance
module.exports = {
  sequelize,
  User,
  ResetToken
}; 