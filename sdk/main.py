from sdk.textClassfication.ALBERTService import ALBERTService
from sdk.preprocess.preprocess_sentences import filter_sentences
from sdk.relationExtraction.relationExtraction import relationExtraction

if __name__ == "__main__":
    '''
        相关性文本分类
    '''
    albert_service = ALBERTService()
    text = ["客户从选项菜单中选择交易类型时，银行系统将会在会话中启动交易用例。",
            "然后客户需要提供适当的详细信息（如涉及的账户、金额）。",
            "如果银行系统批准交易，就会执行完成交易所需的任何步骤（如发放现金或接受信封），然后打印收据。", 
            "然后，银行系统会询问客户是否希望再进行一次交易。",
            "如果银行系统报告客户的PIN码无效，则将执行PIN码无效扩展，然后尝试继续交易。",
            "如果客户的卡因无效密码过多而被扣留，银行系统将中止交易，客户将无法选择再次交易。",
            "如果客户取消交易，或因多次输入无效密码以外的原因导致交易失败，银行系统将显示一个屏幕，告知客户交易失败的原因，然后客户将有机会再次进行交易。",
            "同时，银行系统会将所有发给银行的信息和回复记录在自动取款机的日志中。"]
    relevant_texts = albert_service.get_relevant_sentence_by_albert(text)
    # relevant_texts = text
    print("relevant_texts",relevant_texts)

    '''
        数据预处理：分句；停用词、无用的状语去除
    '''
    filter_texts = filter_sentences(relevant_texts)

    '''
        活动图元素及其关系提取
    '''
    graph = relationExtraction(filter_texts)
    graph._print()
    graph._draw()
    