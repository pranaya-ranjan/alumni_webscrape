from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.main.domain.objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
import os


class Person(Scraper):
    __TOP_CARD = "pv-top-card"
    # __TOP_CARD = "ph5 pb5"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") is None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")
            x = input("please verify the capcha then press any key to continue...")
            self.scrape_not_logged_in(close_on_complete=close_on_complete)

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element_by_class_name(class_name)
            div.find_element_by_tag_name("button").click()
        except Exception as e:
            print('Exception in _click_see_more_by_class_name -\n', class_name, '\n', str(e))
            pass

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        # root = driver.find_element_by_class_name("hidden")
        # root = driver.find_element_by_id("ember905")
        # print(root)
        # self.name = root.find_elements_by_xpath("//section/div/div/div/*/li")[0].text.strip()
        # self.name = "dummy"
        try:
            name = driver.find_element_by_xpath("//*[@id='ember44']/div[2]/div[2]/div/div[1]/h1").text.strip()
            self.name = name

        #            root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
        #                EC.presence_of_element_located(
        #                    (
        #                        By.CLASS_NAME,
        #                        self.__TOP_CARD,
        #                    )
        #               )
        #            )
        #            self.name = root.find_elements_by_xpath("//section/div/div/div/*/li")[0].text.strip()

        except Exception as e:
            print('Error Extracting Name of Person -', str(e))
            self.name = "Dummy"

        # get about

        try:
            #            see_more = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            #                EC.presence_of_element_located(
            #                    (
            #                        By.XPATH,
            #                        "//*[@id='ember92']/div/span",
            #                    )
            #                )
            #            )
            #            driver.execute_script("arguments[0].click();", see_more)
            about = driver.find_element_by_xpath(
                "//*[@class='pv-profile-section pv-about-section artdeco-card p5 mt4 ember-view']/div")
            self.add_about(about.text.strip())

        except Exception as e:
            print('Error Extracting About of Person -', str(e))
            about = None

        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

        # get experience
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/5));"
        )

        ## Click SEE MORE
        self._click_see_more_by_class_name("pv-experience-section__see-more")

        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "experience-section"))
            )
            exp = driver.find_element_by_id("experience-section")
        except:
            exp = None

        if exp is not None:
            for position in exp.find_elements_by_class_name("pv-position-entity"):
                if len(position.find_elements_by_tag_name("h3")) == 1:
                    position_title = position.find_element_by_tag_name("h3").text.strip()

                    try:
                        company = position.find_elements_by_tag_name("p")[1].text.strip()
                    except:
                        company = None

                    try:
                        times = str(
                            position.find_elements_by_tag_name("h4")[0]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                        from_date = " ".join(times.split(" ")[:2])
                        to_date = " ".join(times.split(" ")[3:])
                    except:
                        from_date, to_date = (None, None)

                    try:
                        duration = (
                            position.find_elements_by_tag_name("h4")[1]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                    except:
                        duration = None

                    try:
                        location = (
                            position.find_elements_by_tag_name("h4")[2]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                    except:
                        location = None

                elif len(position.find_elements_by_tag_name("h3")) > 1:
                    try:
                        position_title = " ".join(
                            position.find_elements_by_tag_name("h3")[1].text.split("Title")[1:]).strip()
                    except:
                        position_title = None

                    try:
                        company = " ".join(
                            position.find_elements_by_tag_name("h3")[0].text.split("Company Name")[1:]).strip()
                    except:
                        company = None

                    try:
                        times = str(
                            position.find_elements_by_tag_name("h4")[2]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                        from_date = " ".join(times.split(" ")[:2])
                        to_date = " ".join(times.split(" ")[3:])
                    except:
                        from_date, to_date = (None, None)

                    try:
                        duration = (
                            position.find_elements_by_tag_name("h4")[0]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                    except:
                        duration = None

                    try:
                        location = (
                            position.find_elements_by_tag_name("h4")[4]
                                .find_elements_by_tag_name("span")[1]
                                .text.strip()
                        )
                    except:
                        location = None

                else:
                    position_title = None
                    from_date = None
                    to_date = None
                    duration = None
                    location = None
                    company = None

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)

        # get location
        try:
            location = driver.find_element_by_xpath("//*[@id='ember44']/div[2]/div[2]/div/div[3]/span[1]")
            location = location.text.strip()

        except Exception as e:
            print('Error finding Location -', str(e))
            location = None

        self.add_location(location)

        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get education
        ## Click SEE MORE
        self._click_see_more_by_class_name("pv-education-section__see-more")
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "education-section"))
            )
            edu = driver.find_element_by_id("education-section")
        except Exception as e:
            print('Error finding Education -', str(e))
            edu = None
        if edu is not None:
            for school in edu.find_elements_by_class_name(
                    "pv-profile-section__list-item"
            ):
                university = school.find_element_by_class_name(
                    "pv-entity__school-name"
                ).text.strip()

                try:
                    degree = (
                        school.find_element_by_class_name("pv-entity__degree-name")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    degree = None

                try:
                    times = (
                        school.find_element_by_class_name("pv-entity__dates")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                    from_date, to_date = (times.split(" ")[0], times.split(" ")[2])
                except:
                    from_date, to_date = (None, None)

                try:
                    major = (
                        school.find_element_by_class_name("pv-entity__fos")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    major = None

                education = Education(
                    from_date=from_date, to_date=to_date, degree=degree, major=major
                )
                education.institution_name = university
                self.add_education(education)

        # get interest
        try:

            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-card mt4 p5 ember-view']",
                    )
                )
            )
            interestContainer = driver.find_element_by_xpath(
                "//*[@class='pv-profile-section pv-interests-section artdeco-card mt4 p5 ember-view']"
            )
            for interestElement in interestContainer.find_elements_by_xpath(
                    "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element_by_tag_name("h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

        # get certifications
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-profile-section--certifications-section ember-view']",
                    )
                )
            )
            acc = driver.find_element_by_xpath(
                "//*[@class='pv-profile-section__section-info section-info pv-profile-section__section-info--has-more']"
            )
            for block in acc.find_elements_by_xpath(
                    "//*[@class='pv-profile-section__sortable-item pv-certification-entity ember-view']"):
                certificate = block.find_element_by_class_name(
                    "pv-certifications__summary-info pv-entity__summary-info pv-entity__summary-info--background-section pv-certifications__summary-info--has-extra-details")
                category = certificate.find_element_by_class_name("t-14").text
                title = certificate.find_element_by_class_name(".t-16.t-bold").text
                accomplishment = Accomplishment(category, title)
                self.add_accomplishment(accomplishment)
        except:
            pass

        # get connections
        try:
            raise Exception
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = driver.find_element_by_class_name("mn-connections")
            if connections is not None:
                for conn in connections.find_elements_by_class_name("mn-connection-card"):
                    anchor = conn.find_element_by_class_name("mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element_by_class_name("mn-connection-card__details").find_element_by_class_name(
                        "mn-connection-card__name").text.strip()
                    occupation = conn.find_element_by_class_name(
                        "mn-connection-card__details").find_element_by_class_name(
                        "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    self.add_contact(contact)
        except:
            connections = None

        if close_on_complete:
            driver.quit()

    def scrape_not_logged_in(self, close_on_complete=True, retry_limit=10):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            page = driver.get(self.linkedin_url)
            retry_times = retry_times + 1

        # get name
        self.name = driver.find_element_by_class_name(
            "top-card-layout__title"
        ).text.strip()

        # get experience
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "experience"))
            )
            exp = driver.find_element_by_class_name("experience")
        except:
            exp = None

        if exp is not None:
            for position in exp.find_elements_by_class_name(
                    "experience-item__contents"
            ):
                position_title = position.find_element_by_class_name(
                    "experience-item__title"
                ).text.strip()
                company = position.find_element_by_class_name(
                    "experience-item__subtitle"
                ).text.strip()

                try:
                    times = position.find_element_by_class_name(
                        "experience-item__duration"
                    )
                    from_date = times.find_element_by_class_name(
                        "date-range__start-date"
                    ).text.strip()
                    try:
                        to_date = times.find_element_by_class_name(
                            "date-range__end-date"
                        ).text.strip()
                    except:
                        to_date = "Present"
                    duration = position.find_element_by_class_name(
                        "date-range__duration"
                    ).text.strip()
                    location = position.find_element_by_class_name(
                        "experience-item__location"
                    ).text.strip()
                except:
                    from_date, to_date, duration, location = (None, None, None, None)

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get education
        edu = driver.find_element_by_class_name("education__list")
        for school in edu.find_elements_by_class_name("result-card"):
            university = school.find_element_by_class_name(
                "result-card__title"
            ).text.strip()
            degree = school.find_element_by_class_name(
                "education__item--degree-info"
            ).text.strip()
            try:
                times = school.find_element_by_class_name("date-range")
                from_date = times.find_element_by_class_name(
                    "date-range__start-date"
                ).text.strip()
                to_date = times.find_element_by_class_name(
                    "date-range__end-date"
                ).text.strip()
            except:
                from_date, to_date = (None, None)
            education = Education(from_date=from_date, to_date=to_date, degree=degree)

            education.institution_name = university
            self.add_education(education)

        if close_on_complete:
            driver.close()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
