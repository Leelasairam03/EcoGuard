# Beach Pollution Reporter 🌊

A modern web application for reporting and tracking beach pollution using AI analysis and gamification. Users can upload images of polluted beaches, get AI-powered analysis, and earn points for their contributions to environmental awareness.

## ✨ Features

- **📸 Image Upload**: Drag & drop or click to upload pollution images
- **🗺️ Location Selection**: GPS location or interactive map picker
- **🤖 AI Analysis**: Automated pollution severity scoring (mock implementation)
- **🏆 Gamification**: Point system based on pollution severity
- **📊 Dashboard**: Track your reports and progress
- **📱 Responsive Design**: Modern, mobile-friendly interface
- **🔒 Data Validation**: Comprehensive form validation and error handling

## 🏗️ Project Structure

```
Makeathon/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── models/
│   └── report.py        # Data models and database operations
├── routes/
│   └── main.py          # Route handlers and business logic
├── utils/
│   └── analysis.py      # Analysis utilities and mock AI
├── static/
│   ├── uploads/         # User uploaded images
│   ├── data/            # JSON data storage
│   └── results/         # Analysis results
└── templates/
    ├── upload.html      # Upload form
    ├── result.html      # Analysis results
    ├── dashboard.html   # User dashboard
    └── errors/          # Error pages
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Makeathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Maps**: Leaflet.js (OpenStreetMap)
- **Icons**: Font Awesome 6
- **Styling**: Custom CSS with gradients and animations

## 📱 Usage Guide

### 1. Submit a Report
- Fill in your name and email
- Upload an image of beach pollution
- Select location using GPS or map picker
- Submit for AI analysis

### 2. View Results
- See pollution severity score (0-100)
- Read AI-generated analysis
- Check points earned
- View location details

### 3. Track Progress
- Access your dashboard
- View all submitted reports
- Track total points earned
- Monitor contribution history

## 🔧 Configuration

The application uses a configuration class in `config.py`:

- **File Upload**: Max 16MB, supports PNG, JPG, JPEG, GIF, WEBP
- **Data Storage**: JSON-based storage (easily replaceable with database)
- **Debug Mode**: Configurable via environment variables

## 🔮 Future Enhancements

- **Real AI Integration**: Replace mock analysis with Gemini API or similar
- **Database**: Migrate from JSON to PostgreSQL/MySQL
- **User Authentication**: Login system and user profiles
- **Real-time Updates**: WebSocket integration for live data
- **Mobile App**: React Native or Flutter mobile application
- **API Endpoints**: RESTful API for third-party integrations
- **Analytics**: Advanced reporting and visualization
- **Notifications**: Email/SMS alerts for high-priority reports

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in app.py or kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

2. **File upload errors**
   - Check file size (max 16MB)
   - Verify file format (PNG, JPG, JPEG, GIF, WEBP)
   - Ensure uploads directory has write permissions

3. **Location not working**
   - Allow location access in browser
   - Use map picker as alternative
   - Check internet connection for map tiles

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_DEBUG=True
python app.py
```

## 📊 Data Structure

### Report Object
```json
{
  "filename": "user_image.jpg",
  "latitude": "12.938463",
  "longitude": "74.803913",
  "location_name": "Panambur Beach",
  "score": 75,
  "analysis": "Moderate waste spotted...",
  "reporter_name": "John Doe",
  "reporter_email": "john@example.com",
  "points": 20,
  "timestamp": "2024-01-01T10:00:00"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- OpenStreetMap for map data
- Bootstrap for UI components
- Font Awesome for icons
- Leaflet.js for interactive maps

## 📞 Support

For questions or support, please open an issue in the repository or contact the development team.

---

**Made with ❤️ for environmental awareness and beach cleanup efforts** 