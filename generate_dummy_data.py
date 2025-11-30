import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_STUDENTS = 30
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2024, 11, 20)

# Generate student IDs
STUDENTS = [f"c142201{str(i).zfill(2)}" for i in range(1, NUM_STUDENTS + 1)]

# Assignment configurations with different difficulty levels
ASSIGNMENTS_CONFIG = {
    "Redis List/Set": {
        "difficulty": "easy",
        "pass_threshold": 60,
        "avg_attempts": 2.5,
        "pass_rate": 0.85,
        "score_range": (40, 100),
        "start_offset": 0,  # days from START_DATE
        "duration": 14  # days for submission period
    },
    "Redis Timeseries": {
        "difficulty": "medium",
        "pass_threshold": 60,
        "avg_attempts": 3.2,
        "pass_rate": 0.75,
        "score_range": (20, 100),
        "start_offset": 7,
        "duration": 14
    },
    "MongoDB": {
        "difficulty": "hard",
        "pass_threshold": 60,
        "avg_attempts": 4.0,
        "pass_rate": 0.65,
        "score_range": (10, 100),
        "start_offset": 14,
        "duration": 14
    },
    "Neo4J": {
        "difficulty": "very_hard",
        "pass_threshold": 60,
        "avg_attempts": 4.5,
        "pass_rate": 0.60,
        "score_range": (5, 100),
        "start_offset": 21,
        "duration": 14
    },
    "Big Data Assignment 1": {
        "difficulty": "medium",
        "pass_threshold": 60,
        "avg_attempts": 3.0,
        "pass_rate": 0.80,
        "score_range": (30, 100),
        "start_offset": 28,
        "duration": 10
    },
    "Big Data Assignment 2": {
        "difficulty": "hard",
        "pass_threshold": 60,
        "avg_attempts": 3.8,
        "pass_rate": 0.70,
        "score_range": (15, 100),
        "start_offset": 35,
        "duration": 10
    },
    "Big Data Assignment 3": {
        "difficulty": "very_hard",
        "pass_threshold": 60,
        "avg_attempts": 4.2,
        "pass_rate": 0.65,
        "score_range": (10, 100),
        "start_offset": 42,
        "duration": 10
    }
}

def generate_student_attempts(student_id, config, base_date):
    """Generate attempts for a single student based on their skill level"""
    attempts = []
    
    # Determine student skill level (affects their progression)
    skill_level = np.random.choice(['high', 'medium', 'low'], p=[0.3, 0.5, 0.2])
    
    # Will the student pass?
    will_pass = random.random() < config['pass_rate']
    
    # Determine number of attempts
    if skill_level == 'high':
        num_attempts = max(1, int(np.random.normal(config['avg_attempts'] * 0.7, 1)))
    elif skill_level == 'medium':
        num_attempts = max(1, int(np.random.normal(config['avg_attempts'], 1.5)))
    else:
        num_attempts = max(1, int(np.random.normal(config['avg_attempts'] * 1.3, 2)))
    
    # Cap attempts at reasonable number
    num_attempts = min(num_attempts, 8)
    
    # Generate submission times within the duration period
    submission_times = []
    current_time = base_date + timedelta(
        days=random.uniform(0, config['duration'] * 0.3),
        hours=random.randint(8, 23),
        minutes=random.randint(0, 59)
    )
    
    for i in range(num_attempts):
        submission_times.append(current_time)
        
        # Add random interval between attempts (1-48 hours)
        if i < num_attempts - 1:
            # More attempts tend to be closer together if struggling
            if skill_level == 'low':
                hours_gap = random.uniform(0.5, 24)
            else:
                hours_gap = random.uniform(2, 48)
            
            current_time += timedelta(hours=hours_gap)
    
    # Generate scores with progression
    min_score, max_score = config['score_range']
    
    for i, submit_time in enumerate(submission_times):
        # Calculate score with progression trend
        if skill_level == 'high':
            # High skill students improve quickly
            base_score = min_score + (max_score - min_score) * (0.5 + 0.5 * (i / max(num_attempts - 1, 1)))
            score = int(np.clip(np.random.normal(base_score, 10), min_score, max_score))
        elif skill_level == 'medium':
            # Medium skill students have steady progression
            base_score = min_score + (max_score - min_score) * (0.3 + 0.5 * (i / max(num_attempts - 1, 1)))
            score = int(np.clip(np.random.normal(base_score, 15), min_score, max_score))
        else:
            # Low skill students struggle more
            base_score = min_score + (max_score - min_score) * (0.2 + 0.4 * (i / max(num_attempts - 1, 1)))
            score = int(np.clip(np.random.normal(base_score, 20), min_score, max_score))
        
        # If student should pass and it's later attempts, boost score
        if will_pass and i >= num_attempts - 2:
            score = max(score, config['pass_threshold'] + random.randint(0, 20))
        
        # If student shouldn't pass, keep scores below threshold (but maybe one lucky pass)
        if not will_pass and i < num_attempts - 1:
            score = min(score, config['pass_threshold'] - random.randint(1, 10))
        
        # Determine status
        status = "Lulus" if score >= config['pass_threshold'] else "Tidak Lulus"
        
        attempts.append({
            'Date': submit_time.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
            'NRP': student_id,
            'Nilai': score,
            'Status': status
        })
    
    return attempts

def generate_assignment_data(assignment_name, config):
    """Generate all data for an assignment"""
    print(f"Generating data for {assignment_name}...")
    
    base_date = START_DATE + timedelta(days=config['start_offset'])
    
    all_attempts = []
    
    # Not all students submit every assignment (realistic scenario)
    active_students = random.sample(STUDENTS, k=random.randint(int(NUM_STUDENTS * 0.8), NUM_STUDENTS))
    
    for student in active_students:
        student_attempts = generate_student_attempts(student, config, base_date)
        all_attempts.extend(student_attempts)
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(all_attempts)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Convert back to string format for CSV
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    return df

# Generate data for all assignments
print("=" * 60)
print("GENERATING DUMMY DATA FOR ALL ASSIGNMENTS")
print("=" * 60)
print()

all_datasets = {}

for assignment_name, config in ASSIGNMENTS_CONFIG.items():
    df = generate_assignment_data(assignment_name, config)
    all_datasets[assignment_name] = df
    
    # Print statistics
    print(f"\n{assignment_name} Statistics:")
    print(f"  Total Submissions: {len(df)}")
    print(f"  Unique Students: {df['NRP'].nunique()}")
    print(f"  Pass Rate: {(df['Status'] == 'Lulus').sum() / len(df) * 100:.1f}%")
    print(f"  Avg Score: {df['Nilai'].mean():.1f}")
    print(f"  Score Range: {df['Nilai'].min()} - {df['Nilai'].max()}")
    
    # Save to CSV
    filename = f"{assignment_name.replace('/', '_').replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved to: {filename}")


summary_data = []
for assignment_name, df in all_datasets.items():
    students_passed = df.groupby('NRP')['Status'].apply(lambda x: (x == 'Lulus').any()).sum()
    total_students = df['NRP'].nunique()
    
    summary_data.append({
        'Assignment': assignment_name,
        'Difficulty': ASSIGNMENTS_CONFIG[assignment_name]['difficulty'].upper(),
        'Total Submissions': len(df),
        'Unique Students': total_students,
        'Students Passed': students_passed,
        'Student Pass Rate': f"{students_passed/total_students*100:.1f}%",
        'Submission Pass Rate': f"{(df['Status'] == 'Lulus').sum() / len(df) * 100:.1f}%",
        'Avg Score': f"{df['Nilai'].mean():.1f}",
        'Avg Attempts': f"{df.groupby('NRP').size().mean():.1f}"
    })

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

# Save summary
summary_df.to_csv('SUMMARY_ALL_ASSIGNMENTS.csv', index=False)

for assignment_name in ASSIGNMENTS_CONFIG.keys():
    filename = f"{assignment_name.replace('/', '_').replace(' ', '_')}.csv"
    print(f"{filename}")