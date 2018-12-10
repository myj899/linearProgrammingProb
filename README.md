# LPS

LPS is a user friendly mathematical tool for solving linear programming problems exclusively for feasible solutions. The program implements the simplex algorithm using the numpy module to handle matrices to build the backbone of the solver. The main algorithm is based on the standard form, (maximization problem), and the duality of simplex is used to optimize minization problems. The algorithm does not handle infeasible and infinite solutions.

![Main](./readmeImgs/landingScreenshot.png)

## Table of Contents

1. [Built With](#built-with)
1. [Getting Started](#getting-started)
   1. [Installing Dependencies](#installing-dependencies)
   1. [Development Environment](#development-environment)
1. [Screenshots](#screenshots)
1. [Styling](#styling)
1. [Licensing](#licensing)

## Built With

- [**matplotlib**](https://matplotlib.org/faq/installing_faq.html)
- [**tkinter**](http://www.tkdocs.com/tutorial/install.html)
- [**numpy**](https://scipy.org/install.html)
- [**sympy**](https://scipy.org/install.html)

## Getting Started

### Installing Dependencies

You must install these dependencies using pip:

- [**matplotlib**](https://matplotlib.org/faq/installing_faq.html)
- [**numpy**](https://scipy.org/install.html)
- [**sympy**](https://scipy.org/install.html)

```sh
pip install numpy
```

### Development Environment

To start up the application, from within the root directory:

```sh
python3 ./src/app.py
```

## Screenshots

![RecGuest](./readmeImgs/rec-guest.gif)
![RecUser](./readmeImgs/rec-user.gif)

Once the user signs in, the recommendations changes according to the user's city of residence.

![Search1](./readmeImgs/search-cookingsteak.gif)
![Search2](./readmeImgs/search-cookingsteakforbeginners.gif)

MentorMatch can conduct O(1) search with the power of Redisearch and its inverted indexing methods.

![UserProfile](./readmeImgs/userProfile.gif)

Users can navigate through their profile page for previously booked lessons, upcoming lessons, and lessons that they offer.

![LessonDetails](./readmeImgs/lessonDetails.gif)

Every lesson has a lesson details page where the user can view information on the lesson, the mentor, and the reviews by other users who have taken the lesson in the past.

## Styling

MentorMatch uses the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript/).

## Licensing

MentorMatch uses the [MIT License](LICENSE.md)
