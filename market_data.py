import os
import requests
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List, Tuple, Any, Union
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure requests session with retry
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))

class MarketDataService:
    def __init__(self):
        # Load API keys from environment
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'M5REAHET6BN3DV95')
        self.gold_api_key = os.getenv('GOLD_API_KEY', '')
        
        # Initialize cache with longer TTL
        self.cache = {}
        self.cache_timeout = 600  # 10 minutes cache for prices (increased from 5)
        self.news_cache_timeout = 3600  # 60 minutes for news (increased from 30)
        
        # API rate limiting - be more conservative
        self.last_api_call = 0
        self.min_call_interval = 2.0  # Increased from 1.0 to 2.0 seconds between API calls
        self.daily_calls = 0
        self.last_daily_reset = datetime.now().date()
        self.max_daily_calls = 20  # Stay under the 25/day free tier limit

    def _rate_limit(self) -> None:
        """Enforce rate limiting between API calls and daily limits"""
        # Reset daily counter if it's a new day
        current_date = datetime.now().date()
        if current_date != self.last_daily_reset:
            self.daily_calls = 0
            self.last_daily_reset = current_date
            
        # Check daily limit
        if self.daily_calls >= self.max_daily_calls:
            raise Exception(f'Daily API call limit of {self.max_daily_calls} reached')
            
        # Enforce minimum time between calls
        now = time.time()
        time_since_last_call = now - self.last_api_call
        if time_since_last_call < self.min_call_interval:
            time.sleep(self.min_call_interval - time_since_last_call)
            
        self.last_api_call = time.time()
        self.daily_calls += 1

    def get_gold_price(self) -> Optional[float]:
        """
        Get current gold price using Alpha Vantage as primary source,
        with fallback to other APIs if needed.
        Returns price per troy ounce in USD.
        """
        cache_key = 'gold_price'
        
        # Check cache first
        if cache_key in self.cache and \
           (datetime.now() - self.cache[cache_key]['timestamp']) < timedelta(seconds=self.cache_timeout):
            return self.cache[cache_key]['value']
        
        # Try Alpha Vantage first
        price = self._get_gold_price_alpha_vantage()
        if price is not None:
            self.cache[cache_key] = {
                'value': price,
                'timestamp': datetime.now()
            }
            return price
            
        logger.warning("Alpha Vantage failed, trying fallback API")
        
        # Fallback to previous gold API
        price = self._get_gold_price_fallback()
        if price is not None:
            self.cache[cache_key] = {
                'value': price,
                'timestamp': datetime.now()
            }
            return price
            
        # If all else fails, return None
        logger.error("All gold price APIs failed")
        return None

    def _get_gold_price_alpha_vantage(self) -> Optional[float]:
        """Fetch gold price using Alpha Vantage API"""
        try:
            self._rate_limit()
            
            # Try the COMMODITIES endpoint first (more reliable for XAU/USD)
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=CRYPTO_INTRADAY&"
                f"symbol=XAU&"
                f"market=USD&"
                f"interval=1min&"
                f"outputsize=compact&"
                f"apikey={self.alpha_vantage_key}"
            )
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Try to extract the latest price
            if "Time Series (1min)" in data:
                latest_timestamp = next(iter(data["Time Series (1min)"].values()))
                price = float(latest_timestamp["4. close"])
                logger.info(f"Successfully fetched gold price from Alpha Vantage: ${price:.2f}")
                return price
                
            # Fallback to CURRENCY_EXCHANGE_RATE if the first method fails
            logger.debug("Falling back to CURRENCY_EXCHANGE_RATE endpoint")
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=CURRENCY_EXCHANGE_RATE&"
                f"from_currency=XAU&"
                f"to_currency=USD&"
                f"apikey={self.alpha_vantage_key}"
            )
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "Realtime Currency Exchange Rate" in data:
                rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                logger.info(f"Successfully fetched gold price from Alpha Vantage (FX): ${rate:.2f}")
                return rate
                
            logger.warning(f"Unexpected response from Alpha Vantage: {data}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching from Alpha Vantage: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Alpha Vantage response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in _get_gold_price_alpha_vantage: {e}")
            
        return None

    def _get_gold_price_fallback(self) -> Optional[float]:
        """Fallback method to get gold price from alternative sources"""
        # Try multiple fallback methods in sequence
        methods = [
            self._get_gold_price_goldapi,
            self._get_gold_price_marketstack,
            self._get_gold_price_fixer
        ]
        
        for method in methods:
            try:
                price = method()
                if price is not None:
                    logger.info(f"Successfully fetched gold price using {method.__name__}")
                    return price
            except Exception as e:
                logger.warning(f"Error in {method.__name__}: {e}")
                continue
                
        logger.error("All fallback methods failed")
        return None
        
    def _get_gold_price_goldapi(self) -> Optional[float]:
        """Get gold price from GoldAPI"""
        if not self.gold_api_key:
            return None
            
        url = "https://www.goldapi.io/api/XAU/USD/"
        headers = {
            'x-access-token': self.gold_api_key,
            'Content-Type': 'application/json'
        }
        
        self._rate_limit()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return data.get('price')
    
    def _get_gold_price_marketstack(self) -> Optional[float]:
        """Get gold price from Marketstack (if configured)"""
        marketstack_key = os.getenv('MARKETSTACK_API_KEY')
        if not marketstack_key:
            return None
            
        url = (
            f"http://api.marketstack.com/v1/tickers/XAUUSD/eod/latest"
            f"?access_key={marketstack_key}"
        )
        
        self._rate_limit()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'close' in data:
            return float(data['close'])
        return None
    
    def _get_gold_price_fixer(self) -> Optional[float]:
        """Get gold price from Fixer API (if configured)"""
        fixer_key = os.getenv('FIXER_API_KEY')
        if not fixer_key:
            return None
            
        url = f"http://data.fixer.io/api/latest?access_key={fixer_key}&symbols=XAU,USD"
        
        self._rate_limit()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') and 'rates' in data:
            rates = data['rates']
            if 'XAU' in rates and 'USD' in rates:
                # Convert XAU to USD (XAU is per troy ounce)
                return rates['USD'] / rates['XAU']
        return None

    def get_gold_news(self, limit: int = 5) -> List[Dict]:
        """
        Fetch gold-related news using Alpha Vantage
        Returns a list of news articles
        """
        try:
            # Check cache first
            cache_key = f'gold_news_{limit}'
            if cache_key in self.cache and (datetime.now() - self.cache[cache_key]['timestamp']) < timedelta(minutes=30):
                return self.cache[cache_key]['value']
            
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=XAU&apikey={self.alpha_vantage_key}&limit={limit}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'feed' in data:
                news_items = []
                for item in data['feed'][:limit]:
                    news_items.append({
                        'title': item.get('title', 'No title'),
                        'url': item.get('url', ''),
                        'time_published': item.get('time_published', ''),
                        'source': item.get('source', 'Unknown'),
                        'summary': item.get('summary', 'No summary available')
                    })
                
                # Update cache
                self.cache[cache_key] = {
                    'value': news_items,
                    'timestamp': datetime.now()
                }
                
                return news_items
            else:
                logger.warning("Unexpected response from Alpha Vantage news API")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching gold news: {e}")
            return []

# Singleton instance
market_data_service = MarketDataService()

def format_gold_price(price: float) -> str:
    """Format gold price with currency symbol and 2 decimal places"""
    return f"${price:,.2f}" if price is not None else "Price unavailable"
