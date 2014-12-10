import unittest
import model
import urlparse
import random
import os
import time

class ModelTestCase(unittest.TestCase):

    def setUp(self):

        redis_url = urlparse.urlparse('redis://localhost:6379')
        self.rs = model.FMFRedisHandler(host=redis_url.hostname, port=redis_url.port, db=11, password=redis_url.password)
        assert([] == self.rs.keys("*")), "There are keys in the test Database Teardown will Flush them"

    def test1_add_posts(self):
        """test to confirm that posts are returned form get_recent_posts in correct order (last first)"""

        self.feed = 'test-feed'
        self.post_ids = ['test-post%s' % n for n in range(5)]
        random.shuffle(self.post_ids)

        for post in self.post_ids:
            #create_time = time.time()
            post_dict = {'post_id': post}
            self.rs.set_post(self.feed, post_dict)

        self.post_ids.reverse()

        self.assertEqual(self.post_ids, [post['post_id'] for post in self.rs.get_recent_posts(self.feed)])

    def test2_confirm_no_garbage(self):
        """test to confirm that there are no extra keys in the namespace"""
        #number of expected arguments or keys in the space comes from the 5 test posts + iterator for
        number_of_expected_arguments = 7
        self.assertEqual()


    def tearDown(self):
        pass
        self.rs.flushdb()

if __name__ == "__main__":
    unittest.main(verbosity=2)



