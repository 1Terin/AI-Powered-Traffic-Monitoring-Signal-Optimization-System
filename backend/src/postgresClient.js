const { Sequelize, DataTypes } = require('sequelize');

let sequelize;

function initPostgres() {
  const url = process.env.POSTGRES_URL || 'postgres://postgres:postgres@postgres:5432/trafficdb';
  sequelize = new Sequelize(url, { logging: false });

  const TrafficSummary = sequelize.define('TrafficSummary', {
    intersection: { type: DataTypes.STRING },
    vehicleCount: { type: DataTypes.INTEGER },
    averageSpeed: { type: DataTypes.FLOAT },
    pollutionIndex: { type: DataTypes.FLOAT }
  });

  return { sequelize, TrafficSummary };
}

module.exports = { initPostgres };
