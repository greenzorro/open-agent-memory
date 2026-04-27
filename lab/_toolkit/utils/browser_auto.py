
"""
File: browser_auto.py
Project: routine
Created: 2025-09-23
Author: Victor Cheng
Email: hi@victor42.work
Description: 基于 Playwright 的通用网页自动化工具库
"""

import time
import asyncio
import functools
from typing import Optional, List, Any, Dict, Union, Callable
try:
    from playwright.async_api import async_playwright, Browser, Page, ElementHandle, TimeoutError as PlaywrightTimeoutError
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    ElementHandle = None
    PlaywrightTimeoutError = None
from .basic import *

# 默认浏览器启动参数
DEFAULT_LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=VizDisplayCompositor'
]


# ==============================================================================
# 验证辅助函数 (Validation Helpers)
# ==============================================================================

def validate_page_and_url(page: Page, url: str, default_wait_time: int = 3) -> tuple[bool, int]:
    """验证 page 和 url 参数，返回验证结果和调整后的等待时间"""
    if not page or not url or not isinstance(url, str) or url.strip() == "":
        return False, default_wait_time
    return True, default_wait_time


def validate_page_and_selector(page: Page, selector: str, default_timeout: int = 30) -> tuple[bool, int]:
    """验证 page 和 selector 参数，返回验证结果和调整后的超时时间"""
    if not page or not selector or not isinstance(selector, str) or selector.strip() == "":
        return False, default_timeout
    return True, default_timeout


def validate_timeout_value(timeout: Optional[Union[int, float]], default_timeout: int = 30,
                          allow_zero: bool = False) -> int:
    """验证并调整超时时间值"""
    if timeout is None or not isinstance(timeout, (int, float)):
        return default_timeout
    if allow_zero:
        if timeout < 0:
            return default_timeout
    else:
        if timeout <= 0:
            return default_timeout
    return int(timeout)


# ==============================================================================
# 浏览器工厂函数 (Browser Factory Functions)
# ==============================================================================

async def create_chrome_browser(download_dir: Optional[str] = None, headless: bool = False, playwright_instance=None) -> Browser:
    """
    创建一个带有自定义选项的 Chrome 浏览器实例

    Args:
        download_dir: 下载目录路径（可选）
        headless: 是否以无头模式运行
        playwright_instance: 现有的 playwright 实例（可选）

    Returns:
        配置好的 Browser 实例

    Example:
        >>> async with async_playwright() as p:
        ...     browser = await create_chrome_browser(download_dir='/Users/Downloads', playwright_instance=p)
        ...     page = await browser.new_page()
        ...     await page.goto('https://example.com')
        ...     await browser.close()
    """
    if playwright_instance is None:
        playwright = await async_playwright().start()
    else:
        playwright = playwright_instance

    launch_options = {
        'headless': headless,
        'args': DEFAULT_LAUNCH_ARGS
    }

    browser = await playwright.chromium.launch(**launch_options)
    return browser


async def create_persistent_browser_context(user_data_dir: str, headless: bool = False, playwright_instance=None) -> Browser:
    """
    创建持久化浏览器上下文，适合需要保持登录状态的场景

    Args:
        user_data_dir: 用户数据目录路径
        headless: 是否以无头模式运行
        playwright_instance: 现有的 playwright 实例（可选）

    Returns:
        配置好的 Browser 实例（持久化上下文）

    Example:
        >>> async with async_playwright() as p:
        ...     browser = await create_persistent_browser_context('/tmp/browser_data', playwright_instance=p)
        ...     page = await browser.new_page()
        ...     await page.goto('https://example.com')
        ...     await browser.close()
    """
    if playwright_instance is None:
        playwright = await async_playwright().start()
    else:
        playwright = playwright_instance

    # 组合默认参数和持久化特定参数
    launch_args = DEFAULT_LAUNCH_ARGS.copy()
    launch_args.append('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=headless,
        args=launch_args,
        viewport={'width': 1440, 'height': 900},
        ignore_https_errors=True
    )

    return browser


async def create_page(browser: Browser, download_dir: Optional[str] = None) -> Page:
    """
    创建一个带有下载目录配置的新页面

    Args:
        browser: Browser 实例
        download_dir: 下载目录路径（可选）

    Returns:
        配置好的 Page 实例
    """
    context_options = {
        'viewport': {'width': 1440, 'height': 900},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    if download_dir:
        context_options['accept_downloads'] = True

    context = await browser.new_context(**context_options)
    page = await context.new_page()

    if download_dir:
        # 设置下载行为
        await context.route('**/*', lambda route: route.continue_())

    return page


# ==============================================================================
# 上下文管理器 (Context Manager)
# ==============================================================================

class WebBrowserContext:
    """
    Playwright 浏览器的上下文管理器，支持自动清理资源

    Example:
        >>> async with WebBrowserContext(download_dir='/tmp') as page:
        ...     await navigate_to_url(page, 'https://example.com')
        ...     element = await wait_for_element(page, '.content')
        >>> # 退出上下文时，浏览器和页面会自动关闭

    Example with persistent context (for keeping login session):
    持久化模式示例（用于保持登录会话）：
        >>> async with WebBrowserContext(user_data_dir='/tmp/browser_data') as page:
        ...     await navigate_to_url(page, 'https://example.com')
    """

    def __init__(self, download_dir: Optional[str] = None, headless: bool = False, user_data_dir: Optional[str] = None):
        self.download_dir = download_dir
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.browser = None
        self.page = None
        self.playwright = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        if self.user_data_dir:
            # 持久化上下文模式
            self.browser = await create_persistent_browser_context(
                self.user_data_dir,
                self.headless,
                self.playwright
            )
            # 在持久化模式下，browser context 就是 browser 本身
            self.context = self.browser
            # 持久化上下文自带一个默认页面，但也可以创建新页面
            pages = self.browser.pages
            self.page = pages[0] if pages else await self.browser.new_page()
        else:
            # 标准模式
            self.browser = await create_chrome_browser(self.download_dir, self.headless, self.playwright)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
        
        return self.page

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        cleanup_errors = []

        # 按创建的相反顺序清理资源
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                cleanup_errors.append(f"Context close failed: {e}")

        if self.browser and self.browser != self.context:
            try:
                await self.browser.close()
            except Exception as e:
                cleanup_errors.append(f"Browser close failed: {e}")

        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                cleanup_errors.append(f"Playwright stop failed: {e}")

        # 记录清理过程中的错误
        if cleanup_errors:
            print(f"Resource cleanup warnings: {'; '.join(cleanup_errors)}")


# ==============================================================================
# 导航与等待工具 (Navigation & Wait Utilities)
# ==============================================================================

async def navigate_to_url(page: Page, url: str, wait_time: int = 3) -> bool:
    """
    导航到指定 URL 并等待基本页面加载

    Args:
        page: Page 实例
        url: 目标 URL
        wait_time: 导航后的等待时间（秒）

    Returns:
        如果成功返回 True，否则返回 False

    Example:
        >>> async with async_playwright() as p:
        ...     browser = await p.chromium.launch()
        ...     page = await browser.new_page()
        ...     success = await navigate_to_url(page, 'https://example.com')
        ...     if success:
        ...         print("Navigation successful")
    """
    is_valid, adjusted_wait_time = validate_page_and_url(page, url, wait_time)
    if not is_valid:
        return False

    adjusted_wait_time = validate_timeout_value(wait_time, 3, allow_zero=True)

    try:
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(adjusted_wait_time * 1000)
        return True
    except Exception as e:
        print(f"Error navigating to {url}: {e}")
        return False


async def wait_until(
    condition_fn: Callable,
    timeout: int = 300,
    interval: float = 1,
    description: str = ""
) -> bool:
    """
    通用轮询等待函数，等待任意条件满足

    Args:
        condition_fn: 条件检查函数（同步或异步），返回 True 表示条件满足
        timeout: 最大等待时间（秒）
        interval: 检查间隔（秒）
        description: 描述信息，用于日志输出

    Returns:
        bool: 条件是否在超时前满足

    Example:
        >>> # 等待登录状态（同步条件）
        >>> def is_logged_in():
        ...     return len(page.query_selector_all('.user-info')) > 0
        >>> logged_in = await wait_until(is_logged_in, timeout=300, interval=5, description="登录状态")
        >>>
        >>> # 等待异步条件
        >>> async def check_downloaded():
        ...     return await some_async_check()
        >>> result = await wait_until(check_downloaded, timeout=30, description="异步检查")
    """
    if not callable(condition_fn):
        print(f"[ERROR] wait_until: condition_fn must be callable")
        return False

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            result = await condition_fn() if asyncio.iscoroutinefunction(condition_fn) else condition_fn()
            if result:
                if description:
                    elapsed = time.time() - start_time
                    print(f"[OK] {description}已满足 ({elapsed:.1f}s)")
                return True
        except Exception as e:
            print(f"[ERROR] wait_until条件检查异常: {e}")
            return False

        if time.time() - start_time + interval < timeout:
            await asyncio.sleep(interval)

    if description:
        print(f"[ERROR] 超时：{description}未满足")
    return False


async def wait_for_file_download(download_dir: str, timeout: int = 30, check_interval: float = 0.5) -> bool:
    """
    等待文件下载完成

    Args:
        download_dir: 下载目录路径
        timeout: 最大等待时间（秒）
        check_interval: 检查间隔（秒）

    Returns:
        bool: 是否检测到新文件下载
    """
    if not os.path.exists(download_dir):
        print(f"[ERROR] 下载目录不存在: {download_dir}")
        return False

    # 记录开始时的文件列表和修改时间
    start_files = set(os.listdir(download_dir))
    start_time = time.time()

    print(f"[DEBUG] 等待文件下载到 {download_dir}")

    # 定义文件下载检查条件函数
    async def check_file_downloaded() -> bool:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - start_files

        if new_files:
            print(f"[OK] 检测到新文件下载: {new_files}")
            return True

        # 检查现有文件是否有最近修改的
        for filename in current_files:
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                mtime = os.path.getmtime(filepath)
                # 如果文件在开始等待后（或之前的短时间内）被修改过，说明是下载的文件
                # 允许2秒的时间误差，应对下载速度极快的情况
                if mtime > start_time - 2:
                    print(f"[OK] 检测到文件更新: {filename} (mtime: {mtime}, start: {start_time})")
                    return True

        return False

    # 使用通用轮询等待函数
    return await wait_until(
        condition_fn=check_file_downloaded,
        timeout=timeout,
        interval=check_interval,
        description="文件下载"
    )


async def wait_for_element(page: Page, selector: str, timeout: int = 30) -> Optional[ElementHandle]:
    """
    等待元素出现并返回它

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        timeout: 最大等待时间（秒）

    Returns:
        如果找到则返回 Element，超时或参数无效则返回 None

    Example:
        >>> element = await wait_for_element(page, '.my-class', timeout=10)
        >>> if element:
        ...     print("Element found")
    """
    is_valid, _ = validate_page_and_selector(page, selector, timeout)
    if not is_valid:
        return None

    adjusted_timeout = validate_timeout_value(timeout, 30)

    try:
        element = await page.wait_for_selector(selector, timeout=adjusted_timeout * 1000)
        return element
    except PlaywrightTimeoutError:
        return None
    except Exception as e:
        print(f"Error waiting for element '{selector}': {e}")
        return None


async def wait_for_element_clickable(page: Page, selector: str, timeout: int = 30) -> Optional[ElementHandle]:
    """
    等待元素可点击并返回它

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        timeout: 最大等待时间（秒）

    Returns:
        如果找到且可点击则返回 Element，超时则返回 None

    Example:
        >>> button = await wait_for_element_clickable(page, 'button.submit')
        >>> if button:
        ...     await button.click()
    """
    is_valid, _ = validate_page_and_selector(page, selector, timeout)
    if not is_valid:
        return None

    adjusted_timeout = validate_timeout_value(timeout, 30)

    try:
        element = await page.wait_for_selector(selector, timeout=adjusted_timeout * 1000)
        if element:
            await element.wait_for_element_state('enabled', timeout=adjusted_timeout * 1000)
            return element
        return None
    except PlaywrightTimeoutError:
        return None
    except Exception as e:
        print(f"Error waiting for clickable element '{selector}': {e}")
        return None


async def wait_for_text_in_element(page: Page, selector: str, text: str, timeout: int = 30) -> bool:
    """
    等待指定文本出现在元素中

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        text: 等待的文本
        timeout: 最大等待时间（秒）

    Returns:
        如果文本找到返回 True，超时返回 False

    Example:
        >>> if await wait_for_text_in_element(page, '.status', 'Complete', timeout=10):
        ...     print("Process completed")
    """
    try:
        await page.wait_for_function(
            f'() => {{ const el = document.querySelector("{selector}"); return el && el.textContent.includes("{text}"); }}',
            timeout=timeout * 1000
        )
        return True
    except PlaywrightTimeoutError:
        return False
    except Exception as e:
        print(f"Error waiting for text in element '{selector}': {e}")
        return False


# ==============================================================================
# 元素交互与提取 (Element Interaction & Extraction)
# ==============================================================================

async def click_element(page: Page, selector: str, description: str = "", timeout: int = 30) -> bool:
    """
    安全地点击元素，包含重试逻辑

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        description: 用于日志的可选描述
        timeout: 最大等待时间（秒）

    Returns:
        如果点击成功返回 True，否则返回 False

    Example:
        >>> success = await click_element(page, 'button.submit', 'submit button')
        >>> if success:
        ...     print("Button clicked")
    """
    is_valid, _ = validate_page_and_selector(page, selector, timeout)
    if not is_valid:
        return False

    adjusted_timeout = validate_timeout_value(timeout, 30)

    description = description or selector

    for attempt in range(3):
        try:
            element = await wait_for_element_clickable(page, selector, adjusted_timeout)
            if element:
                await element.click()
                print(f"Clicked {description}")
                await page.wait_for_timeout(1000)  # Brief pause after click
                return True
            else:
                print(f"Element not clickable: {description}")
        except Exception as e:
            print(f"Click attempt {attempt + 1} failed for {description}: {e}")
            await page.wait_for_timeout(1000)
    return False


async def find_elements_by_selector(page: Page, selector: str) -> List[ElementHandle]:
    """
    查找所有匹配 CSS 选择器的元素

    Args:
        page: Page 实例
        selector: CSS 选择器字符串

    Returns:
        匹配元素的列表（如果未找到则为空列表）

    Example:
        >>> links = await find_elements_by_selector(page, 'a.nav-link')
        >>> for link in links:
        ...     text = await link.text_content()
        ...     print(text)
    """
    try:
        elements = await page.query_selector_all(selector)
        return elements
    except Exception as e:
        print(f"Error finding elements by selector '{selector}': {e}")
        return []


async def find_element_by_text(page: Page, selector: str, text: str) -> Optional[ElementHandle]:
    """
    查找包含特定文本的元素

    Args:
        page: Page 实例
        selector: 要在其中搜索的 CSS 选择器
        text: 要搜索的文本内容

    Returns:
        第一个包含该文本的元素，如果未找到则返回 None

    Example:
        >>> tab = await find_element_by_text(page, '.tab', 'Settings')
        >>> if tab:
        ...     await tab.click()
    """
    elements = await find_elements_by_selector(page, selector)
    for element in elements:
        try:
            element_text = await element.text_content()
            if element_text and text in element_text:
                return element
        except Exception as e:
            print(f"Error getting element text: {e}")
    return None


async def get_element_attribute(page: Page, selector: str, attribute: str, timeout: int = 30) -> Optional[str]:
    """
    获取元素的属性值

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        attribute: 要获取的属性名
        timeout: 最大等待时间（秒）

    Returns:
        如果找到则返回属性值，否则返回 None

    Example:
        >>> href = await get_element_attribute(page, 'a.link', 'href')
        >>> if href:
        ...     print(f"Link URL: {href}")
    """
    element = await wait_for_element(page, selector, timeout)
    if element:
        try:
            return await element.get_attribute(attribute)
        except Exception as e:
            print(f"Error getting attribute '{attribute}': {e}")
    return None


async def get_element_attribute_hidden(page: Page, selector: str, attribute: str) -> Optional[str]:
    """
    获取可能被隐藏的元素的属性（不需要可见性）

    Args:
        page: Page 实例
        selector: CSS 选择器字符串
        attribute: 要获取的属性名

    Returns:
        如果找到则返回属性值，否则返回 None

    Example:
        >>> href = await get_element_attribute_hidden(page, 'a.hidden-link', 'href')
        >>> if href:
        ...     print(f"Hidden link URL: {href}")
    """
    try:
        print(f"DEBUG: Looking for hidden element with selector: {selector}")
        element = await page.query_selector(selector)
        if element:
            result = await element.get_attribute(attribute)
            print(f"DEBUG: Hidden element found, attribute '{attribute}': {result}")
            return result
        else:
            print(f"DEBUG: Hidden element not found with selector: {selector}")
        return None
    except Exception as e:
        print(f"Error getting attribute '{attribute}' from hidden element '{selector}': {e}")
        return None


async def scroll_to_element(page: Page, selector: str) -> bool:
    """
    滚动页面以使元素可见

    Args:
        page: Page 实例
        selector: CSS 选择器字符串

    Returns:
        如果成功返回 True，否则返回 False

    Example:
        >>> await scroll_to_element(page, '#bottom-section')
    """
    try:
        element = await page.query_selector(selector)
        if element:
            await element.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)  # Wait for scroll to complete
            return True
        return False
    except Exception as e:
        print(f"Error scrolling to element '{selector}': {e}")
        return False


async def find_and_follow_link_by_prefix(page, prefix: str, description: str = "") -> bool:
    """
    查找并访问指定前缀的链接（支持隐藏元素）

    Args:
        page: Playwright 页面对象
        prefix: 链接 href 前缀
        description: 描述信息

    Returns:
        bool: 是否成功访问链接
    """
    # 查找所有a标签
    links = await find_elements_by_selector(page, "a")

    for link in links:
        href = await link.get_attribute("href")
        if href and href.startswith(prefix):
            print(f"[OK] 找到{description}链接: {href}")

            try:
                # 直接通过JavaScript触发点击，绕过可见性检查
                await page.evaluate("(element) => element.click()", link)
                await page.wait_for_timeout(2000)  # 等待页面跳转
                return True

            except Exception as e:
                # 如果JavaScript点击失败，尝试常规点击
                try:
                    await link.click(force=True)  # 强制点击
                    await page.wait_for_timeout(2000)
                    return True
                except Exception as e2:
                    print(f"[WARNING] 点击{description}链接失败: {e2}")
                    continue

    print(f"[ERROR] 未找到{description}链接")
    return False


# ==============================================================================
# 页面操作 (Page Actions)
# ==============================================================================

async def execute_javascript(page: Page, script: str, *args) -> Any:
    """
    在浏览器中执行 JavaScript

    Args:
        page: Page 实例
        script: 要执行的 JavaScript 代码
        *args: 传递给脚本的参数

    Returns:
        脚本执行结果

    Example:
        >>> result = await execute_javascript(page, "return document.title;")
        >>> print(f"Page title: {result}")
    """
    try:
        return await page.evaluate(script, *args)
    except Exception as e:
        print(f"Error executing JavaScript: {e}")
        return None


async def switch_to_frame(page: Page, selector: str) -> bool:
    """
    切换到 iframe

    Args:
        page: Page 实例
        selector: iframe 的 CSS 选择器

    Returns:
        如果成功返回 True，否则返回 False

    Example:
        >>> if await switch_to_frame(page, 'iframe.content'):
        ...     # Work within iframe
        ...     await page.frame_locator('iframe.content').click('#button')
        ...     await page.frame('iframe.content').evaluate('() => window.scrollTo(0, 0)')
    """
    try:
        frame = await page.query_selector(selector)
        if frame:
            frame_handle = await frame.content_frame()
            if frame_handle:
                return True
        return False
    except Exception as e:
        print(f"Error switching to frame '{selector}': {e}")
        return False


async def take_screenshot(page: Page, filename: str) -> bool:
    """
    截取当前页面的屏幕截图

    Args:
        page: Page 实例
        filename: 截图的输出文件名

    Returns:
        如果成功返回 True，否则返回 False

    Example:
        >>> await take_screenshot(page, 'error_page.png')
    """
    try:
        await page.screenshot(path=filename)
        print(f"Screenshot saved: {filename}")
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False


async def inject_anti_detection_scripts(page: Page):
    """
    注入反检测脚本，移除自动化特征

    Args:
        page: Playwright 页面对象

    Example:
        >>> async with WebBrowserContext() as page:
        ...     await inject_anti_detection_scripts(page)
        ...     await navigate_to_url(page, 'https://example.com')
    """
    await page.add_init_script(
        """
        // 移除自动化特征
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // 移除Chrome自动化特征
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });

        // 模拟真实用户
        window.chrome = {
            runtime: {},
        };
        """
    )


# ==============================================================================
# 系统/特殊工具 (System/Special Utilities)
# ==============================================================================

def get_playwright_download_dir() -> str:
    """
    获取 Playwright 的下载目录

    Returns:
        str: Playwright 下载目录路径
    """
    import os
    import tempfile
    
    # 根据平台选择不同的下载目录查找策略
    if platform_type == 'windows':
        # Windows系统
        temp_dir = tempfile.gettempdir()
        print(f"[DEBUG] 检查临时目录: {temp_dir}")

        # 首先查找专门的下载数字
        download_dirs = []
        for item in os.listdir(temp_dir):
            if item.startswith('playwright-download') and os.path.isdir(os.path.join(temp_dir, item)):
                download_dirs.append(os.path.join(temp_dir, item))

        if download_dirs:
            # 返回最新的下载目录
            download_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            print(f"[DEBUG] 找到Playwright下载目录: {download_dirs[0]}")
            return download_dirs[0]

        # 如果没有专门的下载目录，检查artifacts目录
        artifact_dirs = []
        for item in os.listdir(temp_dir):
            if item.startswith('playwright-artifacts-') and os.path.isdir(os.path.join(temp_dir, item)):
                artifact_dirs.append(os.path.join(temp_dir, item))

        if artifact_dirs:
            # 返回最新的artifacts目录
            artifact_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            print(f"[DEBUG] 使用最新的artifacts目录: {artifact_dirs[0]}")
            return artifact_dirs[0]

        print(f"[DEBUG] 未找到Playwright目录，返回临时目录: {temp_dir}")
        return temp_dir

    elif platform_type == 'mac':
        # macOS系统
        temp_dir = tempfile.gettempdir()
        print(f"[DEBUG] macOS临时目录: {temp_dir}")

        # 在临时目录中查找Playwright相关的下载目录
        playwright_dirs = []
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                # 查找playwright相关的目录
                if ('playwright' in item.lower() and
                    not item.startswith('.') and
                    not item.endswith('.sock')):
                    playwright_dirs.append(item_path)

        if playwright_dirs:
            # 返回最新的Playwright目录
            playwright_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            print(f"[DEBUG] 找到Playwright目录: {playwright_dirs[0]}")
            return playwright_dirs[0]

        # 如果在临时目录中没找到，检查用户缓存目录
        cache_dir = os.path.expanduser("~/Library/Caches")
        if os.path.exists(cache_dir):
            cache_playwright_dirs = []
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path) and 'playwright' in item.lower():
                    cache_playwright_dirs.append(item_path)

            if cache_playwright_dirs:
                cache_playwright_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                print(f"[DEBUG] 在缓存目录找到Playwright目录: {cache_playwright_dirs[0]}")
                return cache_playwright_dirs[0]

        print(f"[DEBUG] 未找到专门的Playwright下载目录，返回临时目录: {temp_dir}")
        return temp_dir

    else:  # wsl, linux, 其他
        # WSL/Linux系统 - 使用Windows的下载目录策略
        temp_dir = tempfile.gettempdir()
        print(f"[DEBUG] WSL/Linux临时目录: {temp_dir}")

        # WSL环境下通常访问Windows的下载目录
        # 可以在这里添加WSL特定的逻辑，暂时使用与Windows相同的策略
        return temp_dir


def batch_open_links_in_browser(links: List[tuple], delay: float = 0.5):
    """
    在用户浏览器中批量打开链接，带延迟控制

    Args:
        links: 链接列表，每个元素为 (title, url) 元组
        delay: 链接之间的延迟秒数

    注意：此函数在 WSL 环境下不支持，因为需要图形界面来运行浏览器。
    WSL 环境下会抛出异常，建议在 Windows 环境中使用此功能。

    Example:
        >>> links = [('小说1', 'https://example.com/1'), ('小说2', 'https://example.com/2')]
        >>> batch_open_links_in_browser(links, delay=0.5)
    """
    import webbrowser
    import time

    if not links:
        print("[INFO] 没有需要打开的链接")
        return

    print(f"[BROWSER] 准备在用户浏览器中打开 {len(links)} 个链接")

    # 准备所有有效的链接
    valid_links = []
    for title, url in links:
        if url and str(url) != 'nan' and url.strip():
            valid_links.append((title, url))
        else:
            print(f"[WARNING] 跳过无效链接: {title}")

    if not valid_links:
        print("[ERROR] 没有有效的链接可以打开")
        return

    print(f"[INFO] 找到 {len(valid_links)} 个有效链接")

    try:
        # 使用webbrowser模块在用户默认浏览器中打开链接
        for i, (title, url) in enumerate(valid_links):
            print(f"[OPEN] ({i+1}/{len(valid_links)}) {title}")
            webbrowser.open_new_tab(url)

            # 短暂延迟，避免浏览器来不及处理
            time.sleep(delay)

        print(f"\n[SUCCESS] 已在浏览器中打开所有链接")

    except Exception as e:
        print(f"[ERROR] 在浏览器中打开链接失败: {e}")
