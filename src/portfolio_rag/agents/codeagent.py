from smolagents import CodeAgent, LiteLLMModel
from omegaconf import DictConfig

def codeagent(cfg: DictConfig):
    model = LiteLLMModel(model_id=cfg.model.name, api_key=cfg.model.api_key)
    agent = CodeAgent(tools=[], model=model, add_base_tools=True, additional_authorized_imports=['pandas'])

    session_prompt = """You have access to the following CSV files:

    1. Clients.csv (path: C:\\Users\\User\\Desktop\\pwc-porfolio-rag\\data\\2025-06-30_Clients.csv)  
    Columns: [ClientID, LastName, FirstName, Income, ClientType]

    2. Collateral.csv (path: C:\\Users\\User\\Desktop\\pwc-porfolio-rag\\data\\2025-06-30_Collateral.csv)  
    Columns: [CollateralID, PropertyMarketValue, PropertyMarketValue_CCY, PropertyType, PropertyAddressCountry, PropertyAddressPostalCodeCity, PropertyAddressStreet, PropertyAddressStreetNumber]

    3. Loans.csv (path: C:\\Users\\User\\Desktop\\pwc-porfolio-rag\\data\\2025-06-30_Loans.csv)  
    Columns: [ClientID, CollateralID, LoanClass, Type, Exposure, ExposureCCY, LGD, Rating, Maturity]

    4. RatingScale.csv (path: C:\\Users\\User\\Desktop\\pwc-porfolio-rag\\data\\RatingScale.csv)  
    Columns: [Rating, Lower Bound PD, Upper Bound PD, Midpoint PD]

    - Always write and execute Python code with pandas to answer queries.
    - Do not reply with a final_answer until you have executed the necessary code.
    - Assume the CSV files exist at the given paths and can be loaded with pandas.read_csv.
    Task:
    - Use pandas to load these CSVs.
    - Perform the necessary joins or transformations to answer the user’s query.
    """

    agent.run(
        session_prompt + " Query: How many clients have more than one loan? What are their client IDs? Are  they secured by the same property or different?"
    )