# import requests
# import json

# class FindRoute:
#     def __init__(self):
#         self.__BASE_URL = 'http://router.project-osrm.org/route/v1/driving/'

#     def find_route(self,center,driver):
#         coordinate = f"{center}:{driver}?verview=simplified"

#         respose = requests.get(self.__BASE_URL+coordinate)
#         print(respose.status_code)
#         data = json.loads(respose.text)
#         print(data)


class DriverRatingCalculator:
    def __init__(self):
        self.total_rating = 0.0
        self.total_trips = 0
        self.total_completed_trips = 0
        self.total_feedback = 0

    def add_trip(self, rating, complated, feedback):
        self.total_trips += 1
        self.total_completed_trips += 1 if complated else 0
        self.total_rating += rating
        if feedback is not None:
            self.total_feedback += feedback

    def calculate_rating(self):
        average_rating = self.total_rating / self.total_completed_trips
        average_feedback = self.total_feedback / self.total_completed_trips
        completion_rate = self.total_completed_trips / self.total_trips
        print(average_feedback,average_rating,completion_rate)

        user_rating_weight = 0.8
        completion_rate_weight = 0.2
        customer_feedback_weight = 0.1

        user_rating_score = average_rating * user_rating_weight
        customer_feedback_score = average_feedback * customer_feedback_weight
        completion_rate_score = (completion_rate * completion_rate_weight) * 5

        print(user_rating_score,customer_feedback_score,completion_rate_score)


        overall_rating = (user_rating_score + completion_rate_score) - customer_feedback_score

        return overall_rating


# Example usage
calculator = DriverRatingCalculator()

# Add completed trips with ratings and feedback
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(5, True, 0)
calculator.add_trip(1, True, 10)

# Calculate the overall rating
# result = calculator.calculate_rating()
# print(f"Overall Driver Rating: {result}")