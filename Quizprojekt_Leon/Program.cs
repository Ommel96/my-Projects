using System.Security.Cryptography.X509Certificates;
using System.Text.Json;


namespace DeserializeFromFile
{
    public class jsonQuestions
    {
        public string? question { get; set; }
        public string? A { get; set; }
        public string? B { get; set; }
        public string? C { get; set; }
        public string? D { get; set; }
        public string? answer { get; set; }

    }

    public class Highscore
    {
        public string Username {get; set;}
        public int Score {get; set;}
        public DateTime Date {get; set;}
        
        
    }

    public class Program
    {
        public static void Main()
        {
            ConsoleKeyInfo cki;

            string fileName = "questions.json";
            string jsonString = File.ReadAllText(fileName);
            var jsonquestions = JsonSerializer.Deserialize<List<jsonQuestions>>(jsonString)!;

            string scoreFilename = "Scores.json";
            string jsonScoreString = File.ReadAllText(scoreFilename);
            var Highscores = JsonSerializer.Deserialize<List<Highscore>>(jsonScoreString)!;

            int amountQuestions = jsonquestions.Count;
            string username = "";
            string input = "";
            bool ready = false;
            bool wantsToPlay = false;
            List<Int32> usedNumbers = new List<Int32>();
            Random rnd = new Random();
            int randomNumber = 0;
            bool contains = false;
            int rolls = 0;
            int playerScore = 0;
            const int defaultPoints = 10;
            int answerTime = 0;

            //how many questions do you want to ask?
            int askedQuestions = 3;


            Console.WriteLine("Please enter your username");
            username = Console.ReadLine();

            do
            {
                Console.WriteLine($"Hello {username}, are you ready?\nType Yes or No");
                input = Console.ReadLine().ToLower();

                if (input == "no")
                {
                    Console.WriteLine($"Well, fair enough. Try again when you feel ready, {username}.");
                    ready = true;
                }

                else if (input == "yes")
                {
                    Console.WriteLine($"Splendid! Let's start right away, {username}.\n");
                    wantsToPlay = true;
                    ready = true;
                }

                else
                {
                    Console.WriteLine("Invalid answer, try again.\n");
                    ready = false;
                }
            } while (ready == false);

            if (wantsToPlay == true)
            {
                do{
                do
                {
                    //generates a random number to ask a random question
                    randomNumber = rnd.Next(0, amountQuestions);

                    //Check if the question has already been asked and reroll until a new number is rolled as long as there are still questions to be asked
                    contains = usedNumbers.Contains(randomNumber);

                } while (contains == true && rolls < askedQuestions);
                //Save the newly rolled number in the usedNumbers array so the question doesnt get asked again.

                usedNumbers.Add(randomNumber);
                rolls += 1;
                answerTime = 10;
                bool timeout = false;


                    {

                    Console.WriteLine($"Question: {jsonquestions[randomNumber].question}");
                    Console.WriteLine($"\tA: {jsonquestions[randomNumber].A}\t\t\tB: {jsonquestions[randomNumber].B}");
                    Console.WriteLine($"\tD: {jsonquestions[randomNumber].C}\t\t\tD: {jsonquestions[randomNumber].D}");
                    Console.WriteLine();
                    Thread.Sleep(5000);
                    Console.WriteLine("Please enter your answer:");

                        do
                        {                         
                            Console.Write($"\r{answerTime}");
                            Thread.Sleep(1000);
                            answerTime -= 1;
                            if(answerTime <= 0)
                            {
                                timeout = true;
                                Console.WriteLine();
                                break;
                            }

                            if (Console.KeyAvailable == true)
                            {
                                Console.WriteLine();
                                break;
                            }

                            
                           
                        } while (Console.KeyAvailable == false || timeout == false) ;
                    
                        if (timeout == true)
                        {
                            Console.WriteLine("Time's Up!");
                            Console.WriteLine("Press any button continue.");
                            Console.ReadKey();
                        }

                        else
                        {
                            cki = Console.ReadKey();
                    

                            if (cki.KeyChar.ToString().ToUpper() == jsonquestions[randomNumber].answer)
                            {
                                playerScore += defaultPoints - (10 - answerTime);
                                Console.WriteLine($"\nThat is correct! +{defaultPoints - (10 - answerTime)} Points\tYour current score is {playerScore}\n");
                            }
                            else Console.WriteLine($"\nToo bad, that is incorrect. The correct answer was {jsonquestions[randomNumber].answer} \n");
                        }
                    

                }
            } while (rolls < askedQuestions);

            Console.WriteLine($"Congratulations {username}, you finished the game with {playerScore} out of {rolls*=10} points!");
            Console.WriteLine();
            Console.WriteLine("Press any button to exit");
            Console.ReadKey();

                // Adding the Score to Json File

                var highscore = new Highscore
            {
                Username = username,
                Score = playerScore,
                Date = DateTime.Today,
            };
            Highscores.Add(highscore);
            string highscoreJson = "Scores.json";
            string jsonStringHS = JsonSerializer.Serialize(Highscores);
            File.WriteAllText(highscoreJson, jsonStringHS);
            }
        }
    }

}