from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from os.path import join, abspath, dirname

"""
guydaniels, reginaneon: 
skill development, implementation, commenting, minor changes

October 17th, 2017
NeonGecko Inc
"""
__author__ = 'guydaniels', 'reginaneon'


class CaffeineWizSkill(MycroftSkill):
    """
        Class name: CaffeineWizSkill

        Purpose: Creates the "CaffeineWizSkill" skill using inherited
                 settings from Mycroft.ai. The skill provides the functionality
                 to inform the user of the caffeine content of the requested
                 drink. Multiple drinks in a row are possible.

                 Sample skill flow:
                 - Hey Mycroft, what's caffeine content of *drink*?
                 - The drink {{drink}} has {{caffeine_content}} milligrams of caffeine in {{drink_size}} ounces.
                   Say "how about another drink" or say "bye".
                 - Goodbye / that's all / exit / we're done

                 - or -

                 - How about *drink*? / what about *drink*?
                 - The drink {{drink}} has {{caffeine_content}} milligrams of caffeine in {{drink_size}} ounces.

    """
    def __init__(self):
        super(CaffeineWizSkill, self).__init__(name="CaffeineWizSkill")
        self.digits = self.config_core.get('system_unit')
        LOG.info(str(self.digits))

        """
        Name: self.drinkList
        Purpose: multi-dimensional array that contains information about most 
                 popular caffeinated drinks and serves as a "database"
                 for the skill.
        """
        self.drinkloc = join(abspath(dirname(__file__)), 'drinkList.txt')

        with open(self.drinkloc) as textFile:
            self.drinkList = [line.strip("\n").split(",") for line in textFile]
            LOG.info(self.drinkList)

    def initialize(self):
        """
        Purpose: register all of the intents using the Mycroft
                 syntax and architecture;
        """
        caffeine_intent = IntentBuilder("CaffeineContentIntent"). \
            require("CaffeineKeyword").require("drink").build()
        self.register_intent(caffeine_intent, self.handle_caffeine_intent)

        goodbye_intent = IntentBuilder("CaffeineContentGoodbyeIntent"). \
            require("GoodbyeKeyword").build()
        self.register_intent(goodbye_intent, self.handle_goodbye_intent)

        """
        Note: after the intents are created, two of the "reply" intents 
              are disabled until the first user response is heard.
        """
        self.disable_intent('CaffeineContentGoodbyeIntent')

    def handle_caffeine_intent(self, message):
        drink = message.data.get("drink", None)
        if drink:
            drink = drink.lower()
        else:
            return

        speech = self._get_drink_text(drink)

        LOG.debug('1- speech = ' + speech)
        self.speak(speech, True)

        """
        Note: at this time the "reply" intents are activated
              again. 
        """
        self.enable_intent('CaffeineContentGoodbyeIntent')

    def handle_goodbye_intent(self, message):
        """
        Note: now the "reply" intents are deactivated,
              since the user specified the end of the skill
              by saying "goodbye"
        """
        self.disable_intent('CaffeineContentGoodbyeIntent')
        LOG.debug('3- Goodbye')
        self.speak('Goodbye. Stay caffeinated!', False)

    @staticmethod
    def _drink_conversion(total, caffeine_oz, oz):
        return int((caffeine_oz/(oz * 29.5735)) * total)

    def _get_drink_text(self, drinkname):
        fndIdx = cnt = 0
        msg = preMsg = ''

        for i in range(len(self.drinkList)):
            tstDrink = self.drinkList[i][0].lower()
            if tstDrink.find(drinkname) != -1:
                fndIdx = i
                break

        if fndIdx > 0:
            for i in range(len(self.drinkList)):
                tstDrink = self.drinkList[i][0].lower()
                if tstDrink.find(drinkname) != -1:
                    
                    oz = float(self.drinkList[i][1])
                    LOG.info(str(oz) + "ounc")
                    caffeine = float(self.drinkList[i][2])
                    LOG.info(str(caffeine) + "caff")

                    msg += 'The drink ' + \
                        self.drinkList[i][0] + ' has '

                    if str(self.digits) != "metric":
                        msg += str(caffeine) + ' milligrams caffeine in '\
                               + str(oz) + ' ounces. '

                    else:
                        if oz <= 8.45351:
                            msg += str(self._drink_conversion(250, caffeine, oz)) + \
                                ' milligrams caffeine in 250 milliliters. '
                        elif oz <= 16.907:
                            msg += str(self._drink_conversion(500, caffeine, oz)) + \
                                   ' milligrams caffeine per 500 milliliters. '
                        else:
                            msg += str(self._drink_conversion(1000, caffeine, oz)) + \
                                   ' milligrams caffeine per liter. '

                    cnt = cnt + 1

        if cnt > 1:
            preMsg = 'I found ' + str(cnt) + ' drinks that match. Here they are:'

        return preMsg + msg + ' Say how about caffeine content of another drink or say goodbye.'

    def stop(self):
        pass


def create_skill():
    return CaffeineWizSkill()
