import asyncio
import json
import re
from playwright.async_api import async_playwright
url = [ "https://amzn.in/d/0cQ3sm7V"]
max_pagination =6


async def extract_data(page) -> list:
    """
    Parsing details from the listing page

    Args:
        page: webpage of the browser

    Returns:
        list: details of homes for sale
    """

    # Initializing selectors and xpaths
    seemore_selector = "//div[@id='reviews-medley-footer']//a"
    div_selector = "[class='a-section celwidget']"
    next_page_selector = "[class='a-last']"
    product_xpath="//*[@id='cm_cr-product_info']/div/div[2]/div/div/div[2]/div[1]/h1/a"
    price_xpath="//*[@id='corePriceDisplay_desktop_feature_div']/div[2]/span/span[1]/span[2]/span/span[2]"
    #number_of_ratings_xpath="//html/body/div[2]/div/div[5]/div[3]/div[4]/div[5]/div/span[3]/a/span"
    style_xpath="//a[contains(@class,'a-size-mini')]"
    #name_xpath = "//*//div[@class='a-profile-content']//span[@class='a-profile-name']"
    rate_xpath = "//*//i[contains(@class,'review-rating')]//span[@class='a-icon-alt']"
    #review_title_xpath = "//a[contains(@class, 'review-title')]/span[2]"
    review_date_xpath = "//span[contains(@class,'review-date')]"
    review_text_xpath = "[data-hook='review-body']"
    #counting number of reviews
    """
    review_numbers = page.locator(number_of_ratings_xpath)
    numb = await review_numbers.inner_text() if await review_numbers.count() else None
    print(numb)
    numbers = re.findall(r'\d+', numb)
    if  numbers:
        nu = int(numbers[0]) / 10
        nu=int(nu)
    else:
    # Handle the case when numb is None (e.g., set it to a default value)
        nu = 5
"""
    product_price = page.locator(price_xpath)
    price_mrp = await product_price.inner_text() if await product_price.count() else None
    # navigating to reviewpage
    review_page_locator = page.locator(seemore_selector)
    await review_page_locator.hover()
    await review_page_locator.click()

    # List to save the details of properties
    amazon_reviews_ratings = []
    await page.wait_for_load_state("load")
    product_name_element = page.locator(product_xpath)
    product_name = await product_name_element.inner_text() if await product_name_element.count() else None
    

    # Paginating through each page
    for _ in range(max_pagination):
        # Waiting for the page to finish loading
        await page.wait_for_load_state("load")
        ##product_name_element = page.locator(product_xpath)
        ##product_name = await product_name_element.inner_text() if await product_name_element.count() else None
        # Extracting the elements
        review_cards = page.locator(div_selector)
        cards_count = await review_cards.count()
        
        for index in range(cards_count):
            
            # Hovering the element to load the price
            inner_element = review_cards.nth(index=index)
            await inner_element.hover()
            inner_element = review_cards.nth(index=index)
            
            # Extracting necessary data
            #product_name=await inner_element.locator(product_xpath).inner_text() if await inner_element.locator(product_xpath).count() else None
            
            review_date = await inner_element.locator(review_date_xpath).inner_text() if await inner_element.locator(review_date_xpath).count() else None
            review_text = await inner_element.locator(review_text_xpath).inner_text() if await inner_element.locator(review_text_xpath).count() else None
            style_name= await inner_element.locator(style_xpath).inner_text() if await inner_element.locator(style_xpath).count() else None
            #name = await inner_element.locator(name_xpath).inner_text() if await inner_element.locator(name_xpath).count() else None
            rate_locator=await inner_element.locator(rate_xpath).all()
            rate = await rate_locator[0].inner_text() if await inner_element.locator(rate_xpath).count() else None
            
            #review_title = await inner_element.locator(review_title_xpath).inner_text() if await inner_element.locator(review_title_xpath).count() else None
            # Removing extra spaces and unicode characters
            """ name = clean_data(name)
            rate = clean_data(rate)
            review_title = clean_data(review_title)
            review_date = clean_data(review_date)
            review_text = clean_data(review_text)"""
           

            data_to_save = {
                
                "product_name":product_name,
                "rate": rate,
                #"review_title": review_title,
                "review_date": review_date,
                "review_text": review_text,
                "product_style":style_name,
                "product_mrp":price_mrp
            }

            amazon_reviews_ratings.append(data_to_save)
        next_page_locator = page.locator(next_page_selector)

        # Check if the "Next Page" button exists
        if await next_page_locator.count() > 0:
            await next_page_locator.hover()
            await next_page_locator.click()
        else:
            break

    save_data(amazon_reviews_ratings, "Data1.json")


async def run(playwright) -> None:
    # Initializing the browser and creating a new page.
    browser = await playwright.firefox.launch(headless=False)
    context = await browser.new_context()
    for i in url:
        page = await context.new_page()

        await page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(120000)

        # Navigating to the homepage
        await page.goto(i, wait_until="domcontentloaded")

        await extract_data(page)

    await context.close()
    await browser.close()


def clean_data(data: str) -> str:
    """
    Cleaning data by removing extra white spaces and Unicode characters

    Args:
        data (str): data to be cleaned

    Returns:
        str: cleaned string
    """
    if not data:
        return ""
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")
    return cleaned_data



def save_data(product_page_data: list, filename: str):
    """Appends a list of dictionaries to an existing JSON file.

    Args:
        product_page_data (list): Details of each product.
        filename (str): Name of the JSON file.
    """
    try:
        with open(filename, "a") as outfile:
            # Append the data to the file
            json.dump(product_page_data, outfile, indent=4)
            outfile.write("\n")  # Add a newline for readability
    except Exception as e:
        print(f"Error appending data to {filename}: {e}")


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())