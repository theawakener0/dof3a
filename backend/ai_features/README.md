# AI Features for Egyptian Educational Social Media Platform

This module provides comprehensive AI integration for an educational social media platform designed for Egyptian students (Middle to Senior grades).

## 🎯 Core Features

### 1. **Personal AI Tutor (Premium Feature)**
- Personalized learning assistance based on student data
- Custom study roadmaps and schedules
- Performance analysis and improvement recommendations
- Conversation history and context awareness
- Egyptian curriculum-aligned guidance

### 2. **1v1 Knockout Competitions**
- AI-generated questions balanced for fair competition
- Automatic difficulty adjustment based on student performance
- Real-time question generation
- Multiple subjects support
- Egyptian education system alignment

### 3. **Content Moderation**
- AI-powered educational content filtering
- Safety and appropriateness checking
- Age-appropriate content verification
- Academic integrity monitoring
- Cultural sensitivity for Egyptian context

### 4. **Study Group Intelligence**
- AI-powered location recommendations for study meetings
- Smart group formation based on compatibility
- Study schedule optimization
- Geographic and cultural context awareness

### 5. **School Group Verification**
- Automatic school affiliation verification
- Access control for school-specific groups
- Student authentication and authorization

## 🏗️ Architecture

```
backend/ai_features/
├── parserdb.py              # Database parser and user data formatting
├── chatai.py                # Core chat AI functionality
├── agents.py                # Specialized AI agents for different features
├── platform_ai_interface.py # Main API interface
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration template
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
cd backend/ai_features

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your actual configuration
```

### 2. Configure Google Vertex AI

```bash
# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### 3. Initialize the AI System

```python
from platform_ai_interface import platform_ai

# Example: Personal AI Tutor
response = platform_ai.chat_with_personal_tutor(
    user_id="student_12345",
    message="I need help with calculus derivatives"
)

# Example: Create Knockout Competition
competition = platform_ai.create_knockout_competition(
    user1_id="student_1",
    user2_id="student_2", 
    subject="Mathematics",
    num_questions=10
)

# Example: Content Moderation
moderation = platform_ai.moderate_post(
    user_id="student_1",
    content="Here's my solution to today's algebra problem..."
)
```

## 📊 Database Integration

### User Profile Structure
```python
@dataclass
class UserProfile:
    user_id: str
    name: str
    grade_level: str          # "Grade 10", "Grade 11", etc.
    school_type: str          # "Public", "Private", "International"
    learning_style: str       # "Visual", "Auditory", "Kinesthetic"
    preferred_subjects: List[str]
    weak_subjects: List[str]
    study_hours_per_day: float
    target_universities: List[str]
```

### Course Progress Tracking
```python
@dataclass
class CourseProgress:
    course_id: str
    course_name: str
    subject: str
    current_progress: float   # 0-100%
    average_grade: float
    quiz_scores: List[float]
    assignment_scores: List[float]
    attendance_rate: float
    time_spent_hours: float
    difficulty_level: str
    last_activity: datetime
```

## 🎯 Platform Features Integration

### 1. Personal AI Tutor Integration
```python
# Premium subscription feature
def chat_with_tutor(user_id: str, message: str):
    return platform_ai.chat_with_personal_tutor(user_id, message)

def generate_roadmap(user_id: str, subject: str):
    return platform_ai.generate_study_roadmap(user_id, subject)
```

### 2. Knockout Competition System
```python
# Fair competition matching
def create_competition(user1_id: str, user2_id: str, subject: str):
    return platform_ai.create_knockout_competition(user1_id, user2_id, subject)

def find_opponents(user_id: str, subject: str):
    return platform_ai.get_balanced_opponents(user_id, subject)
```

### 3. Content Moderation Pipeline
```python
# Automatic content filtering
def post_content(user_id: str, content: str):
    moderation = platform_ai.moderate_post(user_id, content)
    if moderation["approved"]:
        # Publish content
        return publish_post(content)
    else:
        # Handle rejection/review
        return handle_moderation_result(moderation)
```

### 4. Study Group Features
```python
# Smart group formation
def create_study_group(user_id: str, subject: str):
    return platform_ai.form_study_group(user_id, subject)

def recommend_locations(group_members: List[str], subject: str):
    return platform_ai.recommend_study_locations(group_members, subject)
```

## 🔐 Subscription & Business Model

### Free Tier
- Basic AI content moderation
- Standard knockout competitions
- Basic study group features
- Limited personal tutor interactions (5/day)

### Premium Tier ($9.99/month)
- Unlimited personal AI tutor access
- Advanced study roadmap generation
- Priority competition matching
- Enhanced study group recommendations
- Performance analytics and insights

### Enterprise Tier (Schools)
- Bulk subscriptions for students
- Administrative dashboard
- Advanced analytics
- Custom AI model training
- Priority support

## 🌍 Egyptian Education Context

### Curriculum Alignment
- Follows Egyptian Ministry of Education curriculum
- Supports Arabic and English languages
- Grade-specific content (Grade 7-12)
- University preparation focus (Egyptian universities)

### Cultural Considerations
- Islamic values and cultural sensitivity
- Local geography and context awareness
- Egyptian social norms and educational practices
- Arabic language support and terminology

## 🛡️ Security & Privacy

### Data Protection
- Student data encryption at rest and in transit
- GDPR-compliant data handling
- Parental consent for minors
- Secure authentication and authorization

### Content Safety
- Multi-layer content moderation
- Anti-bullying detection
- Academic integrity monitoring
- Age-appropriate content filtering

## 📈 Performance & Scalability

### Optimization Features
- Response caching for common queries
- User data caching with TTL
- Asynchronous processing for heavy operations
- Load balancing for high-traffic scenarios

### Monitoring
- AI model performance tracking
- User engagement metrics
- Error logging and alerting
- Cost optimization monitoring

## 🔧 Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_moderation.py
```

### Development Setup
```bash
# Enable debug mode
export DEBUG=True

# Use development database
export DATABASE_URL="sqlite:///dev.db"

# Mock AI responses for testing
export MOCK_AI_RESPONSES=True
```

## 📚 API Documentation

### Main Interface Methods

#### Personal AI Tutor
- `chat_with_personal_tutor(user_id, message, context=None)`
- `generate_study_roadmap(user_id, subject=None, timeframe="month")`
- `analyze_student_performance(user_id)`

#### Knockout Competitions
- `create_knockout_competition(user1_id, user2_id, subject, num_questions=10)`
- `get_balanced_opponents(user_id, subject)`

#### Content Moderation
- `moderate_post(user_id, content)`
- `moderate_reel(user_id, content)`
- `moderate_comment(user_id, comment)`

#### Study Groups
- `form_study_group(user_id, subject, preferred_size=4)`
- `recommend_study_locations(group_members, subject, duration=2)`

#### School Groups
- `verify_school_access(user_id, school_group_id)`

#### Analytics
- `get_platform_insights(user_id)`

## 🚀 Deployment

### Production Environment
```bash
# Set production environment
export ENVIRONMENT=production

# Configure production database
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Set up monitoring
export SENTRY_DSN="your-sentry-dsn"

# Configure Redis for caching
export REDIS_URL="redis://your-redis-host:6379/0"
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "platform_ai_interface"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For technical support or questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for Egyptian students' educational success**
