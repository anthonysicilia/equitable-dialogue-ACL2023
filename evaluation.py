from collections import defaultdict
import json
import gzip

import random; random.seed(42)

from string import punctuation

CHECK = False

MALE = ['he', 'man', 'him', 'his', 'guy', 
    'boy', 'men', 'guys', 'boys']

FEMALE = ['she', 'woman', 'her', 'hers', 'gal', 
    'girl', 'women', 'gals', 'girls']

def ismale(s):
    for word in s.split():
        w = word.lower().strip(punctuation)
        if w in MALE:
            return True
    return False

def isfemale(s):
    for word in s.split():
        w = word.lower().strip(punctuation)
        if w in FEMALE:
            return True
    return False

def isprotected(s, verbalizers):
    for word in s.split():
        w = word.lower().strip(punctuation)
        if w in verbalizers:
            return True
    return False

def process_image_maps(maps, verbalizers):
    images_w_protected = []
    for mp in maps:
        for image, arr in mp.items():
            idx = 0
            protected = [False]
            for (s, i) in arr:
                if i > idx:
                    protected.append(False)
                    idx += 1
                protected[idx] = protected[idx] or isprotected(s, verbalizers)
            if all(protected): images_w_protected.append(image)
    return images_w_protected

def process_human_questions():

    paths = ['data/guesswhat.test.jsonl.gz',
        'data/guesswhat.train.jsonl.gz',
        'data/guesswhat.valid.jsonl.gz']
    
    questions = dict()
    for file_name in paths:
        with gzip.open(file_name) as file:
            file = list(file)
            random.seed(42)
            random.shuffle(file)
            for line in file:
                game = json.loads(line.decode("utf-8"))
                imid = int(game['image']['id'])
                if imid in questions:
                    idx = questions[imid][-1][-1] + 1
                else:
                    idx = 0
                if imid not in questions:
                    questions[imid] = []
                for turn in game['qas']:
                    questions[imid].append((turn['question'], idx))

    return questions

class Labels:

    def __init__(self, verbalizers):
        questions = process_human_questions()
        protected = process_image_maps([questions], verbalizers)
        self.protected = set(protected)
        self.not_protected = set(questions.keys()).difference(self.protected)
    
    def isprotected(self, image):
        return image in self.protected
    
    def exists(self, image):
        return image in self.protected or image in self.not_protected
    
    def ratio(self, counts=False):
        if counts:
            a = len(self.protected)
            b = len(self.not_protected)
            return a / b, a, b
        else:
            return len(a) / len(b)
    
    def downsmaple(self, seed=42):
        r, p, np = self.ratio(counts=True)
        assert np > p
        np = int(r * np)
        n = np + p
        not_protected = []
        protected = []
        random.seed(seed)
        rnp = random.sample(self.not_protected, len(self.not_protected))
        rp = random.sample(self.protected, len(self.protected))
        while len(protected) + len(not_protected) < n:
            if len(rnp) < 1:
                rnp = random.sample(self.not_protected, len(self.not_protected))
            if len(rp) < 1:
                rp = random.sample(self.protected, len(self.protected))
            if random.random() < 0.5:
                not_protected.append(rnp.pop())
            else:
                protected.append(rp.pop())
        self.protected = set(protected)
        self.not_protected = set(not_protected)

if __name__ == '__main__':

    for P, V in [('F', FEMALE), ('M', MALE)]:
        labels = Labels(verbalizers=V)
        r, p, np = labels.ratio(counts=True)
        print(f'P={P}')
        print(f'Ratio (P/NP): {r:.4f}')
        print(f'Count (P):', p)
        print(f'Count (NP):', np)
        labels.downsmaple()
        r, p, np = labels.ratio(counts=True)
        print(f'Bal. Ratio (P/NP): {r:.4f}')
        print(f'Bal. Count (P):', p)
        print(f'Bal. Count (NP):', np)

        # NOTE: add your own inference files here
        file_names = [
            # 'logs/GamePlay/b0s2e962022_04_13_14_29/test_GPinference_b0s2e96_2022_04_13_14_29.json',
            # 'logs/GamePlay/b1s2e862022_04_13_14_29/test_GPinference_b1s2e86_2022_04_13_14_29.json',
            # 'logs/GamePlay/fair-b1s2e732022_09_24_10_47/test_GPinference_fair-b1s2e73_2022_09_24_10_47.json'

            'logs/GamePlay/b0s2e992022_04_13_12_55/test_GPinference_b0s2e99_2022_04_13_12_55.json',
            'logs/GamePlay/b1s2e992022_04_13_12_40/test_GPinference_b1s2e99_2022_04_13_12_40.json',
            'logs/GamePlay/fair-b1s2e992022_09_24_10_47/test_GPinference_fair-b1s2e99_2022_09_24_10_47.json',
        ]

        examples = {fn : set() for fn in file_names}
        example_questions = {fn : defaultdict(list) for fn in file_names}
        for file_name in file_names:
            hum_eval_idx = 50
            random.seed(42)
            with open(file_name) as file:
                counts = {
                    'e | 0' : 0,
                    'e | 1' : 0,
                    'm0' : 0,
                    'm1' : 0}
                games = json.load(file)
                for g in games.keys():
                    game = games[g]
                    imid = int(game['image'].split('_')[-1]
                        .split('.')[0].lstrip('0'))
                    protected = labels.isprotected(imid)
                    exists = labels.exists(imid)
                    if not exists:
                        continue
                    questions = game['gen_dialogue'].split('?')

                    # NOTE: used for example figures
                    if imid == 266697:
                        with open('ski-example.txt', 'a') as out:
                            out.write(file_name + '\n')
                            out.write(P + '\n')
                            out.write(str(imid) + '\n')
                            for q in questions:
                                out.write(q + '\n')

                    # NOTE: used to sample examples for human evaluation
                    # if random.random() < 0.1 and hum_eval_idx < 100:
                    #     with open('bias-hum-eval.txt', 'a') as out:
                    #         out.write(file_name + '\n')
                    #         out.write(P + '\n')
                    #         out.write(str(imid) + '\n')
                    #         for q in questions:
                    #             out.write(q + '\n')
                    #     hum_eval_idx += 1

                    v = False
                    for question in questions:
                        if isprotected(question, V): v = True
                    e = protected != v

                    # NOTE: For the paper, we balanced protected attributes
                    # among images once for the whole dataset (see top of __main__). 
                    # B/c skews across train/val/test in the original GuessWhat?!
                    # data, this does not ensure the test set (by itself) is 
                    # balanced. The "corrected version" below is a patch to 
                    # make the test set (by itself) balanced.
                    # Results/takeaways are not impacted by this change,
                    # but it may be important for future works, so 
                    # we are documenting it here.
                    ##################################################
                    # corrected version
                    ###################
                    ## 0.5 for patch because test set skew is 1:2
                    # rcorrection = random.random() < 0.5
                    # if P == 'F':
                    #     if protected:
                    #         counts['e | 1'] += e
                    #         counts['m1'] += 1
                    #     elif rcorrection:
                    #         counts['e | 0'] += e
                    #         counts['m0'] += 1
                    # else:
                    #     if protected and rcorrection:
                    #         counts['e | 1'] += e
                    #         counts['m1'] += 1
                    #     elif not protected:
                    #         counts['e | 0'] += e
                    #         counts['m0'] += 1
                    ###################
                    # Patched Results
                    #########
                    # CL Baseline
                    # > AP gap (F): 53.2 | TD (F): 37.7 | AP gap (M): 26.4 | TD (M): 30.5
                    # DS CL Baseline
                    # > AP gap (F): 35.7 | TD (F): 35.3 | AP gap (M): 3.2 | TD (M): 30.6
                    # Ours
                    # > AP gap (F): 31.1 | TD (F): 31.3 | AP gap (M): 16.3 | TD (M): 27.8
                    ##################################################
                    # Original paper version
                    ################
                    if protected:
                        counts['e | 1'] += e
                        counts['m1'] += 1
                    else:
                        counts['e | 0'] += e
                        counts['m0'] += 1
                    ####################
                    # Original Paper Results
                    ##########
                    # CL Baseline 
                    # > AP gap (F): 52.6 | TD (F): 28.8 | AP gap (M): 23.7 | TD (M): 33.5
                    # DS CL Baseline
                    # > AP gap (F): 35.8 | TD (F): 28.9 | AP gap (M): 2.3 | TD (M): 30.7
                    # Ours
                    # > AP gap (F): 29.1 | TD (F): 27.2 | AP gap (M): 14.7 | TD (M): 29.7
                    ##################################################
            
            print('=' * 20)
            print(file_name)
            ap_pr_0 = counts['e | 0'] / counts['m0']
            ap_pr_1 = counts['e | 1'] / counts['m1']
            # NOTE: used to pick 0.5 for patch
            # print('0 count', counts['m0']); print('1 count', counts['m1'])
            print(f'AP gap ({P}): {100 * abs(ap_pr_0 - ap_pr_1):.1f}')
            td = (counts['e | 0'] + counts['e | 1']) \
                / (counts['m0'] + counts['m1'])
            print(f'TD ({P}): {100 * abs(0 - td):.1f}')

