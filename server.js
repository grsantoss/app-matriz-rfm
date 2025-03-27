const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files from the frontend folder
app.use(express.static('frontend'));

// API endpoint for AI insights
app.post('/api/ai-insights', (req, res) => {
  // This would integrate with an AI service in a real application
  // For now, we'll return mock data
  const insights = `
    # Análise Estratégica de Segmentação RFM
    
    ## Visão Geral
    Sua análise RFM demonstra uma segmentação clara dos clientes, revelando oportunidades para estratégias personalizadas.
    
    ## Principais Insights
    
    - **Campeões (High RFM)**: Representam 12% dos seus clientes mas geram 40% da receita. Recomendamos programas de fidelidade exclusivos e comunicação personalizada.
    
    - **Clientes em Risco**: 15% de seus clientes de alto valor estão diminuindo atividade. Implementar uma campanha de reativação específica pode recuperar até 30% deste grupo.
    
    - **Clientes Hibernando**: 22% dos clientes não realizaram compras nos últimos 6 meses. Estratégias de desconto incremental podem reativar estes clientes.
    
    - **Novos Clientes Promissores**: 8% de novos clientes demonstram alta frequência. Incentive a próxima compra com ofertas exclusivas para consolidar o relacionamento.
    
    ## Próximos Passos Recomendados
    
    1. Implementar campanha de recompensa para os Campeões
    2. Criar sequência de emails personalizados para Clientes em Risco
    3. Desenvolver programa de reativação com incentivos progressivos para Hibernando
    4. Monitorar mensalmente a migração entre segmentos
  `;

  // Simulate processing delay
  setTimeout(() => {
    res.json({
      success: true,
      insights: insights
    });
  }, 2000);
});

// API endpoint for login 
app.post('/api/auth/login', (req, res) => {
  // Mock login authentication
  const { email, password } = req.body;
  
  // In a real application, would validate against database
  if (email && password) {
    res.json({
      success: true,
      user: {
        id: 1,
        name: 'Usuário Teste',
        email: email
      },
      token: 'mock-jwt-token'
    });
  } else {
    res.status(401).json({
      success: false,
      message: 'Email ou senha inválidos'
    });
  }
});

// API endpoint for registration
app.post('/api/auth/register', (req, res) => {
  // Mock registration
  const { name, email, password } = req.body;
  
  // In a real application, would validate and save to database
  if (name && email && password) {
    res.json({
      success: true,
      message: 'Cadastro realizado com sucesso!'
    });
  } else {
    res.status(400).json({
      success: false,
      message: 'Dados de cadastro incompletos'
    });
  }
});

// Default route to serve the frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'login.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Access the application at http://localhost:${PORT}`);
}); 