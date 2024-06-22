import random
from tqdm import tqdm
import streamlit as st

antagonist_muscle_groups = {
    "Upper Chest": ["Upper Back"],
    "Middle Chest": ["Upper Back", "Lats"],
    "Traps": ["Lats"],
    "Upper Back": ["Upper Chest", "Middle Chest"],
    "Lower Back": [],
    "Lats": ["Middle Chest", "Traps", "Front Delt", "Mid Delt"],
    "Front Delt": ["Rear Delt", "Lats"],
    "Mid Delt": ["Lats"],
    "Rear Delt": ["Front Delt"],
    "Biceps": ["Triceps"],
    "Triceps": ["Biceps"],
    "Quads": ["Hamstrings"],
    "Hamstrings": ["Quads"],
    "Glutes": [],
    "Calves": []
}

protagonist_muscle_groups = {
    'Upper Chest': ['Middle Chest', 'Front Delt'],
    'Middle Chest': ['Upper Chest', 'Front Delt'],
    'Traps': ['Upper Back'],
    'Upper Back': ['Lats'],
    'Lower Back': [],
    'Lats': ['Upper Back'],
    'Front Delt': ['Mid Delt', 'Middle Chest', 'Upper Chest'],
    'Mid Delt': ['Front Delt', 'Middle Chest', 'Upper Chest'],
    'Rear Delt': ['Upper Back'],
    'Biceps': ['Upper Back', 'Lats'],
    'Triceps': ['Upper Chest', 'Middle Chest', 'Front Delt'],
    'Quads': ['Glutes'],
    'Hamstrings': ['Glutes'],
    'Glutes': ['Quads', 'Hamstrings'],
    'Calves': []
}

exercises = {
    'Upper Chest': ['Dumbbell Incline Chest Fly', 'Upper Chest Cable Crossover', 'Incline Bench Press'],
    'Middle Chest': ['Dumbbell Chest Fly', 'Pec Deck', 'Bench Press', 'Cable Crossover', 'Dips'],
    'Traps': ['Dumbbell Shrugs', 'Barbell Shrugs'],
    'Upper Back': ['Barbell Row', 'Machine Row', 'Seated Row', 'Dumbbell Row', 'Chest Supported Row'],
    'Lower Back': ['Deadlift', 'Good Morning', 'Hyperextension'],
    'Lats': ['Lat Pulldown', 'Pull-Up', 'Pullover', 'Cable Pullover'],
    'Front Delt': ['Front Raise', 'Military Press', 'Seated Dumbbell Press', 'Cable Front Raise'],
    'Mid Delt': ['Dumbbell Lateral Raise', 'Cable Lateral Raise', 'Machine Lateral Raise', 'Cross Body Cable Raise'],
    'Rear Delt': ['Reverse Peck Deck', 'Face Pull', 'Rear Delt Cable Fly', 'Bent Over Reverse Fly'],
    'Biceps': ['EZ Bicep Curl', 'Hammer Curl', 'Preacher Curl', 'Behind-the-Back Cable Curl', 'Incline Dumbbell Curl'],
    'Triceps': ['Tricep Extension', 'Overheach Tricep Extension', 'Skull Crushers', 'Tricep Pushdown'],
    'Quads': ['Squat', 'Leg Press', 'Hack Squat', 'Leg Extension'],
    'Hamstrings': ['Leg Curl', 'Romanian Deadlift'],
    'Glutes': ['Glute Bridge', 'Hip Thrust', 'Bulgarian Spit Squat'],
    'Calves': ['Calf Raise', 'Seated Calf Raise']
}


#workout_days = [1, 2, 3, 4, 5]
#priorities = {'Upper Chest': 3, 'Middle Chest': 1, 'Traps': 2, 'Upper Back': 3, 'Lower Back': 2, 'Lats': 2, 'Front Delt': 1, 'Mid Delt': 3, 'Rear Delt': 2, 'Biceps': 3, 'Triceps': 3, 'Quads': 1, 'Hamstrings': 1, 'Glutes': 1, 'Calves': 2}

# Define a function to calculate the fitness of a workout plan
def fitness(workout_plan, priorities, workout_days):
    # Reward for evenly distributing workouts throughout the week
    distribution_reward = 0
    last_workout_day = {muscle_group: None for muscle_group in priorities.keys()}
    for day in workout_days:
        for i, muscle_group in enumerate(workout_plan[day]):
            if last_workout_day[muscle_group] is not None:
                # The reward is the difference between the current day and the last workout day
                distribution_reward += 4 * (day - last_workout_day[muscle_group])
            last_workout_day[muscle_group] = day

    # Reward for placing antagonist muscle groups as the next exercise
    # Penalty for placing protagonist muscle groups as the next exercise
    antagonist_reward = 0
    protagonist_penalty = 0
    for day, muscle_groups in workout_plan.items():
        for i, muscle_group in enumerate(muscle_groups[:-1]):  # Exclude the last exercise
            next_exercise = muscle_groups[i + 1]
            if next_exercise in antagonist_muscle_groups[muscle_group]:
                antagonist_reward += 2
            if next_exercise in protagonist_muscle_groups[muscle_group]:
                protagonist_penalty += 15
    # Penalty for repeating the same muscle group in a single day
    repetition_penalty = 0
    for day, muscle_groups in workout_plan.items():
        if len(muscle_groups) != len(set(muscle_groups)):
            repetition_penalty += 100  # Adjust this value as needed

    return distribution_reward + antagonist_reward - protagonist_penalty - repetition_penalty

def generate_workout_plan(workout_days, muscle_groups, fitness, priorities, antagonist_muscle_groups):
    best_workout_plan = None
    best_fitness = 0

    # Create a progress bar
    progress_bar = st.progress(0)

    for i in tqdm(range(10)):  # Number of rounds
        # Update the progress bar
        progress_bar.progress((i + 1) / 10)

        # Initialize a random workout plan
        random.shuffle(muscle_groups)
        workout_plan = {day: [] for day in workout_days}
        for i, muscle_group in enumerate(muscle_groups):
            day = workout_days[i % len(workout_days)]
            workout_plan[day].append(muscle_group)

        # Perform the local search
        current_fitness = fitness(workout_plan, priorities, workout_days)
        for _ in range(300000):  # Number of iterations
            # Randomly select two days and two muscle groups
            day1, day2 = random.sample(workout_days, 2)
            muscle_group1, muscle_group2 = random.choice(workout_plan[day1]), random.choice(workout_plan[day2])

            # Swap the muscle groups between the days
            workout_plan[day1].remove(muscle_group1)
            workout_plan[day1].append(muscle_group2)
            workout_plan[day2].remove(muscle_group2)
            workout_plan[day2].append(muscle_group1)

            # If the new workout plan is better, keep it
            new_fitness = fitness(workout_plan, priorities, workout_days)
            if new_fitness > current_fitness:
                current_fitness = new_fitness
            else:  # Otherwise, undo the swap
                workout_plan[day1].remove(muscle_group2)
                workout_plan[day1].append(muscle_group1)
                workout_plan[day2].remove(muscle_group1)
                workout_plan[day2].append(muscle_group2)

        # If the current workout plan is the best so far, keep it
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_workout_plan = workout_plan

    return best_workout_plan, best_fitness

def reorder_workout_plan(workout_plan, priorities, antagonist_muscle_groups):
    reordered_workout_plan = {}
    for day, muscle_groups in workout_plan.items():
        reordered_muscle_groups = []
        while muscle_groups:
            # Find the muscle group with the highest priority
            highest_priority_muscle_group = max(muscle_groups, key=priorities.get)
            muscle_groups.remove(highest_priority_muscle_group)
            reordered_muscle_groups.append(highest_priority_muscle_group)

            # Find the first antagonist for the highest priority muscle group
            antagonists = antagonist_muscle_groups[highest_priority_muscle_group]
            for antagonist in antagonists:
                if antagonist in muscle_groups:
                    muscle_groups.remove(antagonist)
                    reordered_muscle_groups.append(antagonist)
                    break  # Only add the first antagonist

        reordered_workout_plan[day] = reordered_muscle_groups

    return reordered_workout_plan

def populate_workout_plan(workout_plan, exercises):
    populated_workout_plan = {}
    for day, muscle_groups in workout_plan.items():
        day_exercises = []
        for muscle_group in muscle_groups:
            exercise = random.choice(exercises[muscle_group])
            day_exercises.append(exercise)
        populated_workout_plan[day] = day_exercises
    return populated_workout_plan


def app(exercises):
    best_workout_plan = {}
    reordered_workout_plan = {}
    populated_workout_plan = {}
    st.title('Workout Program Generator')
    st.header('Choose workout days')
    # Get user inputs
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    workout_days = [i+1 for i, day in enumerate(days) if st.toggle(day)]
    if not workout_days:
        st.error('Please select at least one workout day.')
        return
    st.header('Choose how much to train each muscle group')
    priorities = {}
    muscles = ['Upper Chest', 'Middle Chest', 'Traps', 'Upper Back', 'Lower Back', 'Lats', 'Front Delt', 'Mid Delt', 'Rear Delt', 'Biceps', 'Triceps', 'Quads', 'Hamstrings', 'Glutes', 'Calves']
    for muscle in muscles:
        priority = st.number_input(f'How many times a week do you want to train {muscle}? (0-7)', min_value=0, max_value=7)
        priorities[muscle] = priority
    muscle_groups = []
    for muscle_group, times in priorities.items():
        muscle_groups.extend([muscle_group] * times)
    if st.button('Generate Workout Plan'):
        best_workout_plan, best_fitness = generate_workout_plan(workout_days, muscle_groups, fitness, priorities, antagonist_muscle_groups)
        if best_workout_plan is not None:
            reordered_workout_plan = reorder_workout_plan(best_workout_plan, priorities, antagonist_muscle_groups)
            populated_workout_plan = populate_workout_plan(reordered_workout_plan, exercises)
             # Print the best workout plan
            st.subheader('Workout Plan Outline')
            cols = st.columns(len(workout_days))
            for i, (day, muscle_groups) in enumerate(reordered_workout_plan.items()):
                cols[i].markdown(f"**Day {day}:**")  # Print the day once
                for muscle_group in muscle_groups:
                    cols[i].markdown(f"{muscle_group}")
                

            # Print the populated workout plan
            st.subheader('Workout Plan Example')
            cols = st.columns(len(workout_days))
            for i, (day, exercises) in enumerate(populated_workout_plan.items()):
                cols[i].markdown(f"**Day {day}:**")  # Print the day once
                for exercise in exercises:
                    cols[i].markdown(f"{exercise}")
                
            
if __name__ == '__main__':
    app(exercises)


