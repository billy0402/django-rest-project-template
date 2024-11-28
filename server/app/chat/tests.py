import typing as t

from channels import testing
from selenium import webdriver
from selenium.webdriver.common import action_chains, by, keys
from selenium.webdriver.support import wait


class ChatTests(testing.ChannelsLiveServerTestCase):
    serve_static = True  # emulate StaticLiveServerTestCase

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        try:
            cls.driver = webdriver.Firefox()
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self) -> None:
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_1")

            self._switch_to_window(0)
            self._post_message("hello")
            wait.WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 1 from window 1",
            )
            self._switch_to_window(1)
            wait.WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 2 from window 1",
            )
        finally:
            self._close_all_new_windows()

    def test_when_chat_message_posted_then_not_seen_by_anyone_in_different_room(
        self,
    ) -> None:
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_2")

            self._switch_to_window(0)
            self._post_message("hello")
            wait.WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 1 from window 1",
            )

            self._switch_to_window(1)
            self._post_message("world")
            wait.WebDriverWait(self.driver, 2).until(
                lambda _: "world" in self._chat_log_value,
                "Message was not received by window 2 from window 2",
            )
            assert (
                "hello" not in self._chat_log_value
            ), "Message was improperly received by window 2 from window 1"
        finally:
            self._close_all_new_windows()

    # === Utility ===

    def _enter_chat_room(self, room_name: str) -> None:
        self.driver.get(self.live_server_url + "/chat/")
        action_chains.ActionChains(self.driver).send_keys(
            room_name, keys.Keys.ENTER
        ).perform()
        wait.WebDriverWait(self.driver, 2).until(
            lambda _: room_name in self.driver.current_url
        )

    def _open_new_window(self) -> None:
        self.driver.execute_script('window.open("about:blank", "_blank");')
        self._switch_to_window(-1)

    def _close_all_new_windows(self) -> None:
        while len(self.driver.window_handles) > 1:
            self._switch_to_window(-1)
            self.driver.execute_script("window.close();")
        if len(self.driver.window_handles) == 1:
            self._switch_to_window(0)

    def _switch_to_window(self, window_index: int) -> None:
        self.driver.switch_to.window(self.driver.window_handles[window_index])

    def _post_message(self, message: str) -> None:
        action_chains.ActionChains(self.driver).send_keys(
            message, keys.Keys.ENTER
        ).perform()

    @property
    def _chat_log_value(self) -> str:
        chat_log = self.driver.find_element(by=by.By.CSS_SELECTOR, value="#chat-log")
        return t.cast(str, chat_log.get_property("value"))
