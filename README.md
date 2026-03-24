# IBM Cloudant Data Retrieval System

A high-performance data retrieval system for IBM Cloudant with a modern web interface, real-time progress tracking, and retrieval history.

## 🚀 Features

- **Web-Based Interface** - Modern React UI with IBM Carbon Design System
- **Real-Time Progress** - Live updates on retrieval status and speed
- **Retrieval History** - Track all past retrievals with performance metrics
- **Resume Capability** - Checkpoint system for interrupted retrievals
- **Async Processing** - High-performance concurrent data fetching
- **Date Range Selection** - Flexible date-based filtering
- **Graceful Cancellation** - Stop retrievals cleanly at any time

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- IBM Cloudant account with API credentials

## ⚡ Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd Dormant-ID
```

### 2. Configure Credentials

```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.example frontend/.env

# Edit .env with your Cloudant credentials
nano .env
```

### 3. Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 4. Start Servers

```bash
# Use the convenient script
./scripts/start_servers.sh

# Or manually:
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && npm start
```

### 5. Access Application

Open http://localhost:3000 in your browser

## 📁 Project Structure

```
Dormant-ID/
├── backend/              # Flask REST API server
│   ├── app.py           # Main API endpoints
│   └── requirements.txt # Python dependencies
├── frontend/            # React web interface
│   ├── src/
│   │   ├── App.js      # Main React component
│   │   └── App.scss    # Styling
│   └── package.json    # Node dependencies
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── api_client.py        # Cloudant API client
├── orchestrator.py      # Data orchestration logic
├── .env.example         # Environment template
└── README.md           # This file
```

## 🔧 Configuration

### Backend (.env)

```bash
API_BASE_URL=https://your-instance.cloudant.com/database/_design/view/_view/name
API_KEY=your-api-key
API_PASSWORD=your-api-password
```

### Frontend (frontend/.env)

```bash
REACT_APP_API_URL=http://localhost:5001
```

## 📊 API Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - Current retrieval status
- `GET /api/history` - Retrieval history
- `POST /api/retrieve` - Start data retrieval
- `POST /api/stop` - Stop current retrieval
- `POST /api/reset` - Reset status

## 🎯 Usage

1. **Select Date Range** - Use date pickers to choose start and end dates
2. **Start Retrieval** - Click "Start Retrieval" button
3. **Monitor Progress** - Watch real-time updates on records and speed
4. **View History** - Check past retrievals in the history section
5. **Stop if Needed** - Click "Stop Retrieval" to cancel gracefully

## 📈 Performance

- **Page Size**: 5,000 records per request
- **Rate Limit**: 10 requests/second (default)
- **Concurrent Processing**: 3 months at a time
- **Expected Speed**: Varies based on network and API performance

## 🔒 Security

- API credentials stored in `.env` files (gitignored)
- No hardcoded credentials in source code
- Sensitive data excluded from version control
- See `docs/GIT_SETUP_GUIDE.md` for details

## 📚 Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get started quickly
- **[Git Setup](docs/GIT_SETUP_GUIDE.md)** - Secure Git configuration
- **[Performance Guide](docs/PERFORMANCE_AND_HISTORY_GUIDE.md)** - Optimization tips
- **[Full Stack Setup](docs/FULL_STACK_SETUP.md)** - Detailed setup instructions

## 🛠️ Scripts

- `scripts/start_servers.sh` - Start both servers
- `scripts/restart_servers.sh` - Restart servers
- `scripts/verify_git_security.sh` - Check Git security
- `scripts/setup_fullstack.sh` - Initial setup

## 🐛 Troubleshooting

### Backend Won't Start
- Check Python version: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Verify `.env` file exists with correct credentials

### Frontend Won't Start
- Check Node version: `node --version`
- Install dependencies: `cd frontend && npm install`
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

### No Data Retrieved
- Verify Cloudant credentials in `.env`
- Check network connectivity
- Review backend logs: `tail -f backend.log`

## 📝 Output

Retrieved data is saved to `output/` directory:
- Format: JSONL (JSON Lines)
- Filename: `data_YYYY_MM.jsonl`
- One JSON object per line

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run security check: `./scripts/verify_git_security.sh`
5. Submit a pull request

## 📄 License

[Your License Here]

## 👤 Author

[Your Name]

## 🙏 Acknowledgments

- IBM Carbon Design System
- IBM Cloudant
- React and Flask communities

---

For detailed documentation, see the `docs/` directory.